import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, List, Any
import joblib
import os
import logging

from schemas import PredictionRequest, PredictionResponse, DistrictPrediction, PredictionSummary, BaselineResponse
from models import HistoricalData

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.demand_model = None
        self.supply_model = None
        self.model_metrics = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize ML models with training data"""
        try:
            # Load or create training data
            training_data = self._generate_training_data()
            
            # Train models
            self._train_models(training_data)
            
            self.is_initialized = True
            logger.info("ML Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML Service: {e}")
            raise
    
    def _generate_training_data(self) -> pd.DataFrame:
        """Generate synthetic training data for ML models"""
        np.random.seed(42)
        
        districts = [
            "Northern Plains", "Coastal Valley", "Mountain Ridge", 
            "Central Plateau", "Eastern Hills", "Western Desert",
            "Southern Delta", "Highland Region", "River Basin", "Urban Center"
        ]
        
        data = []
        for district in districts:
            for year in range(2019, 2024):
                for month in range(1, 13):
                    # Generate correlated features
                    rainfall = np.random.normal(100, 30)  # mm
                    temperature = np.random.normal(25, 5)  # celsius
                    population = np.random.normal(200, 50)  # thousands
                    
                    # Generate realistic demand (higher with population and temperature)
                    demand = (population * 0.5 + 
                             temperature * 2 + 
                             np.random.normal(0, 10))
                    demand = max(demand, 10)  # minimum demand
                    
                    # Generate realistic supply (higher with rainfall)
                    supply = (rainfall * 0.8 + 
                             np.random.normal(50, 15))
                    supply = max(supply, 5)  # minimum supply
                    
                    # Calculate stress level
                    stress_ratio = demand / supply
                    if stress_ratio > 1.2:
                        stress_level = "Deficit"
                        stress_score = 2
                    elif stress_ratio > 0.8:
                        stress_level = "Moderate" 
                        stress_score = 1
                    else:
                        stress_level = "Surplus"
                        stress_score = 0
                    
                    data.append({
                        'district_name': district,
                        'year': year,
                        'month': month,
                        'rainfall': rainfall,
                        'temperature': temperature,
                        'population': population,
                        'demand': demand,
                        'supply': supply,
                        'stress_level': stress_level,
                        'stress_score': stress_score
                    })
        
        return pd.DataFrame(data)
    
    def _train_models(self, data: pd.DataFrame):
        """Train RandomForest models for demand and supply prediction"""
        # Prepare features
        features = ['rainfall', 'temperature', 'population', 'year', 'month']
        X = data[features]
        
        # Train demand model
        y_demand = data['demand']
        X_train, X_test, y_train, y_test = train_test_split(X, y_demand, test_size=0.2, random_state=42)
        
        self.demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.demand_model.fit(X_train, y_train)
        
        # Evaluate demand model
        y_pred = self.demand_model.predict(X_test)
        self.model_metrics['demand'] = {
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
        
        # Train supply model
        y_supply = data['supply']
        X_train, X_test, y_train, y_test = train_test_split(X, y_supply, test_size=0.2, random_state=42)
        
        self.supply_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.supply_model.fit(X_train, y_train)
        
        # Evaluate supply model
        y_pred = self.supply_model.predict(X_test)
        self.model_metrics['supply'] = {
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
        
        logger.info(f"Models trained successfully. Metrics: {self.model_metrics}")
    
    async def get_baseline_prediction(self, region_id: str, latest_data: HistoricalData) -> BaselineResponse:
        """Get baseline prediction for a region"""
        if not self.is_initialized:
            raise RuntimeError("ML Service not initialized")
        
        # Use latest historical data as baseline
        districts = self._get_districts_for_region(region_id)
        predictions = []
        
        for district in districts:
            # Prepare features for prediction
            features = np.array([[
                latest_data.rainfall,
                latest_data.temperature,
                latest_data.region.population / 1000,  # convert to thousands
                2024,  # current year
                6  # mid-year month
            ]])
            
            predicted_demand = self.demand_model.predict(features)[0]
            predicted_supply = self.supply_model.predict(features)[0]
            
            # Calculate stress level
            stress_ratio = predicted_demand / predicted_supply if predicted_supply > 0 else 2
            if stress_ratio > 1.2:
                stress_level = "Deficit"
            elif stress_ratio > 0.8:
                stress_level = "Stable"
            else:
                stress_level = "Surplus"
            
            predictions.append({
                "district_name": district["name"],
                "predicted_demand": round(predicted_demand, 2),
                "predicted_supply": round(predicted_supply, 2),
                "stress_level": stress_level,
                "coordinates": district["coordinates"]
            })
        
        # Calculate summary
        high_risk_count = sum(1 for p in predictions if p["stress_level"] == "Deficit")
        avg_stress = sum(p["predicted_demand"] / p["predicted_supply"] 
                        for p in predictions if p["predicted_supply"] > 0) / len(predictions)
        
        summary = {
            "total_districts": len(predictions),
            "high_risk_count": high_risk_count,
            "average_stress_score": round(avg_stress, 2)
        }
        
        return BaselineResponse(
            region_id=region_id,
            predictions=predictions,
            summary=summary
        )
    
    async def predict_scenario(self, request: PredictionRequest, db) -> PredictionResponse:
        """Generate predictions for a scenario"""
        if not self.is_initialized:
            raise RuntimeError("ML Service not initialized")
        
        # Get latest historical data for the region
        latest_data = db.query(HistoricalData)\
            .filter(HistoricalData.region_id == request.region_id)\
            .order_by(HistoricalData.year.desc())\
            .first()
        
        if not latest_data:
            raise ValueError(f"No historical data found for region {request.region_id}")
        
        # Apply scenario changes
        adjusted_rainfall = latest_data.rainfall * (1 + request.rainfall_change_percent / 100)
        adjusted_temperature = latest_data.temperature + request.temperature_change
        adjusted_population = (latest_data.region.population / 1000) * (1 + request.population_change_percent / 100)
        
        districts = self._get_districts_for_region(request.region_id)
        predictions = []
        
        for district in districts:
            # Prepare features for prediction
            features = np.array([[
                adjusted_rainfall,
                adjusted_temperature,
                adjusted_population,
                request.year,
                6  # mid-year month
            ]])
            
            predicted_demand = self.demand_model.predict(features)[0]
            predicted_supply = self.supply_model.predict(features)[0]
            
            # Calculate stress level
            stress_ratio = predicted_demand / predicted_supply if predicted_supply > 0 else 2
            if stress_ratio > 1.2:
                stress_level = "Deficit"
            elif stress_ratio > 0.8:
                stress_level = "Stable"
            else:
                stress_level = "Surplus"
            
            prediction = DistrictPrediction(
                district_name=district["name"],
                predicted_demand=round(predicted_demand, 2),
                predicted_supply=round(predicted_supply, 2),
                stress_level=stress_level,
                coordinates=district["coordinates"]
            )
            predictions.append(prediction)
        
        # Calculate summary
        high_risk_count = sum(1 for p in predictions if p.stress_level == "Deficit")
        avg_stress = sum(p.predicted_demand / p.predicted_supply 
                        for p in predictions if p.predicted_supply > 0) / len(predictions)
        
        summary = PredictionSummary(
            total_districts=len(predictions),
            high_risk_count=high_risk_count,
            average_stress_score=round(avg_stress, 2),
            model_accuracy=self.model_metrics
        )
        
        return PredictionResponse(predictions=predictions, summary=summary)
    
    def _get_districts_for_region(self, region_id: str) -> List[Dict[str, Any]]:
        """Get districts for a region with coordinates"""
        # Mock district data - in production this would come from database
        district_mapping = {
            "district_1": [
                {"name": "North Plains A", "coordinates": [28.5, 77.5]},
                {"name": "North Plains B", "coordinates": [28.3, 77.7]},
            ],
            "district_2": [
                {"name": "Coastal Valley A", "coordinates": [27.5, 76.5]},
                {"name": "Coastal Valley B", "coordinates": [27.3, 76.7]},
            ],
            "district_3": [
                {"name": "Mountain Ridge A", "coordinates": [29.5, 78.5]},
                {"name": "Mountain Ridge B", "coordinates": [29.3, 78.7]},
            ],
            "district_4": [
                {"name": "Central Plateau A", "coordinates": [27.5, 77.5]},
                {"name": "Central Plateau B", "coordinates": [27.3, 77.7]},
            ],
            "district_5": [
                {"name": "Eastern Hills A", "coordinates": [28.5, 79.5]},
                {"name": "Eastern Hills B", "coordinates": [28.3, 79.7]},
            ]
        }
        
        return district_mapping.get(region_id, [
            {"name": "Default District", "coordinates": [28.0, 77.0]}
        ])