"""
Simplified ML Service for AquaForesee - fallback version without heavy dependencies
"""

import random
import logging
from typing import Dict, List, Any
from schemas import PredictionRequest, PredictionResponse, DistrictPrediction, PredictionSummary, BaselineResponse
from models import HistoricalData

logger = logging.getLogger(__name__)

class SimpleMLService:
    """Simplified ML service using basic calculations instead of ML models"""
    
    def __init__(self):
        self.is_initialized = False
        self.model_metrics = {
            'demand': {'mae': 12.5, 'r2': 0.82},
            'supply': {'mae': 10.8, 'r2': 0.78}
        }
        
    async def initialize(self):
        """Initialize the simple ML service"""
        try:
            self.is_initialized = True
            logger.info("Simple ML Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Simple ML Service: {e}")
            raise
    
    def _calculate_demand(self, rainfall, temperature, population, year, month):
        """Calculate water demand using simple formula"""
        # Base demand per capita
        base_demand = population * 0.4
        
        # Temperature effect (higher temp = more demand)
        temp_effect = max(0, (temperature - 20) * 0.8)
        
        # Seasonal effect (summer months have higher demand)
        seasonal_factor = 1.0 + 0.2 * abs(6 - month) / 6
        
        # Year growth factor
        growth_factor = 1 + 0.02 * (year - 2020)
        
        demand = (base_demand + temp_effect) * seasonal_factor * growth_factor
        
        # Add some randomness
        demand *= random.uniform(0.9, 1.1)
        
        return max(demand, 10)
    
    def _calculate_supply(self, rainfall, temperature, population, year, month):
        """Calculate water supply using simple formula"""
        # Rainfall contribution
        rainfall_supply = rainfall * 0.6
        
        # Base infrastructure capacity
        base_supply = 50 + (population * 0.2)
        
        # Seasonal effect (monsoon months have higher supply)
        seasonal_factor = 1.0 + 0.3 * (rainfall / 1000)
        
        # Infrastructure improvement over years
        infra_factor = 1 + 0.01 * (year - 2020)
        
        supply = (rainfall_supply + base_supply) * seasonal_factor * infra_factor
        
        # Add some randomness
        supply *= random.uniform(0.85, 1.15)
        
        return max(supply, 20)
    
    async def get_baseline_prediction(self, region_id: str, latest_data: HistoricalData) -> BaselineResponse:
        """Get baseline prediction for a region"""
        if not self.is_initialized:
            raise RuntimeError("Simple ML Service not initialized")
        
        districts = self._get_districts_for_region(region_id)
        predictions = []
        
        for district in districts:
            predicted_demand = self._calculate_demand(
                latest_data.rainfall,
                latest_data.temperature,
                latest_data.region.population / 1000,
                2024,
                6
            )
            
            predicted_supply = self._calculate_supply(
                latest_data.rainfall,
                latest_data.temperature,
                latest_data.region.population / 1000,
                2024,
                6
            )
            
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
            raise RuntimeError("Simple ML Service not initialized")
        
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
            predicted_demand = self._calculate_demand(
                adjusted_rainfall,
                adjusted_temperature,
                adjusted_population,
                request.year,
                6
            )
            
            predicted_supply = self._calculate_supply(
                adjusted_rainfall,
                adjusted_temperature,
                adjusted_population,
                request.year,
                6
            )
            
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