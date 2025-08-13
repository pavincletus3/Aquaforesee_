import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import os
import json

def generate_training_data():
    """Generate comprehensive training data for water demand/supply prediction"""
    np.random.seed(42)
    
    districts = [
        "Northern Plains", "Coastal Valley", "Mountain Ridge", 
        "Central Plateau", "Eastern Hills", "Western Desert",
        "Southern Delta", "Highland Region", "River Basin", "Urban Center"
    ]
    
    data = []
    
    for district in districts:
        # District-specific characteristics
        district_factors = {
            "Northern Plains": {"base_pop": 250, "rainfall_factor": 1.2, "temp_factor": 1.0},
            "Coastal Valley": {"base_pop": 180, "rainfall_factor": 1.5, "temp_factor": 0.9},
            "Mountain Ridge": {"base_pop": 120, "rainfall_factor": 1.8, "temp_factor": 0.8},
            "Central Plateau": {"base_pop": 300, "rainfall_factor": 1.0, "temp_factor": 1.1},
            "Eastern Hills": {"base_pop": 95, "rainfall_factor": 1.6, "temp_factor": 0.85},
            "Western Desert": {"base_pop": 80, "rainfall_factor": 0.4, "temp_factor": 1.3},
            "Southern Delta": {"base_pop": 220, "rainfall_factor": 1.4, "temp_factor": 1.0},
            "Highland Region": {"base_pop": 110, "rainfall_factor": 1.7, "temp_factor": 0.75},
            "River Basin": {"base_pop": 280, "rainfall_factor": 1.3, "temp_factor": 0.95},
            "Urban Center": {"base_pop": 450, "rainfall_factor": 0.8, "temp_factor": 1.2}
        }
        
        factors = district_factors[district]
        
        for year in range(2015, 2024):
            for month in range(1, 13):
                # Seasonal variations
                seasonal_rainfall = 1.0 + 0.5 * np.sin(2 * np.pi * (month - 3) / 12)
                seasonal_temp = 25 + 8 * np.sin(2 * np.pi * (month - 3) / 12)
                
                # Generate correlated features with realistic variations
                base_rainfall = 80 * factors["rainfall_factor"] * seasonal_rainfall
                rainfall = max(0, np.random.normal(base_rainfall, base_rainfall * 0.3))
                
                base_temp = seasonal_temp * factors["temp_factor"]
                temperature = np.random.normal(base_temp, 3)
                
                # Population growth over years
                population_growth = 1 + 0.02 * (year - 2015)  # 2% annual growth
                population = factors["base_pop"] * population_growth * np.random.normal(1, 0.05)
                
                # Water demand calculation (realistic correlations)
                # Higher demand with: more population, higher temperature, urban areas
                base_demand = population * 0.4  # Base per capita demand
                temp_effect = max(0, (temperature - 20) * 0.8)  # Increased demand in hot weather
                seasonal_demand = 1.0 + 0.2 * np.sin(2 * np.pi * (month - 1) / 12)  # Peak in summer
                
                demand = (base_demand + temp_effect) * seasonal_demand * np.random.normal(1, 0.1)
                demand = max(demand, 10)  # Minimum demand
                
                # Water supply calculation (realistic correlations)
                # Higher supply with: more rainfall, better infrastructure
                rainfall_supply = rainfall * 0.6  # Conversion factor
                base_supply = 50 + (population * 0.2)  # Base infrastructure capacity
                
                supply = (rainfall_supply + base_supply) * np.random.normal(1, 0.15)
                supply = max(supply, 20)  # Minimum supply
                
                # Calculate stress metrics
                stress_ratio = demand / supply if supply > 0 else 2.0
                
                if stress_ratio > 1.3:
                    stress_level = "Deficit"
                    stress_score = 2
                elif stress_ratio > 0.9:
                    stress_level = "Moderate"
                    stress_score = 1
                else:
                    stress_level = "Surplus"
                    stress_score = 0
                
                # Add some noise and edge cases
                if np.random.random() < 0.05:  # 5% chance of extreme events
                    if np.random.random() < 0.5:  # Drought
                        supply *= 0.3
                        stress_level = "Deficit"
                        stress_score = 2
                    else:  # Flood/excess supply
                        supply *= 2.0
                        stress_level = "Surplus"
                        stress_score = 0
                
                data.append({
                    'district_name': district,
                    'year': year,
                    'month': month,
                    'rainfall': round(rainfall, 2),
                    'temperature': round(temperature, 2),
                    'population': round(population, 2),
                    'demand': round(demand, 2),
                    'supply': round(supply, 2),
                    'stress_level': stress_level,
                    'stress_score': stress_score,
                    'stress_ratio': round(stress_ratio, 3)
                })
    
    return pd.DataFrame(data)

def train_models():
    """Train and evaluate ML models"""
    print("Generating training data...")
    data = generate_training_data()
    
    print(f"Generated {len(data)} training samples")
    print(f"Data shape: {data.shape}")
    print(f"Districts: {data['district_name'].nunique()}")
    print(f"Years: {data['year'].min()} - {data['year'].max()}")
    
    # Prepare features
    features = ['rainfall', 'temperature', 'population', 'year', 'month']
    X = data[features]
    
    # Train demand prediction model
    print("\nTraining demand prediction model...")
    y_demand = data['demand']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_demand, test_size=0.2, random_state=42)
    
    demand_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    demand_model.fit(X_train, y_train)
    
    # Evaluate demand model
    y_pred_demand = demand_model.predict(X_test)
    demand_metrics = {
        'mae': mean_absolute_error(y_test, y_pred_demand),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_demand)),
        'r2': r2_score(y_test, y_pred_demand)
    }
    
    # Cross-validation for demand model
    cv_scores_demand = cross_val_score(demand_model, X, y_demand, cv=5, scoring='r2')
    demand_metrics['cv_r2_mean'] = cv_scores_demand.mean()
    demand_metrics['cv_r2_std'] = cv_scores_demand.std()
    
    print(f"Demand Model - MAE: {demand_metrics['mae']:.2f}, RMSE: {demand_metrics['rmse']:.2f}, R²: {demand_metrics['r2']:.3f}")
    print(f"Demand Model - CV R² Mean: {demand_metrics['cv_r2_mean']:.3f} ± {demand_metrics['cv_r2_std']:.3f}")
    
    # Train supply prediction model
    print("\nTraining supply prediction model...")
    y_supply = data['supply']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_supply, test_size=0.2, random_state=42)
    
    supply_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    supply_model.fit(X_train, y_train)
    
    # Evaluate supply model
    y_pred_supply = supply_model.predict(X_test)
    supply_metrics = {
        'mae': mean_absolute_error(y_test, y_pred_supply),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_supply)),
        'r2': r2_score(y_test, y_pred_supply)
    }
    
    # Cross-validation for supply model
    cv_scores_supply = cross_val_score(supply_model, X, y_supply, cv=5, scoring='r2')
    supply_metrics['cv_r2_mean'] = cv_scores_supply.mean()
    supply_metrics['cv_r2_std'] = cv_scores_supply.std()
    
    print(f"Supply Model - MAE: {supply_metrics['mae']:.2f}, RMSE: {supply_metrics['rmse']:.2f}, R²: {supply_metrics['r2']:.3f}")
    print(f"Supply Model - CV R² Mean: {supply_metrics['cv_r2_mean']:.3f} ± {supply_metrics['cv_r2_std']:.3f}")
    
    # Feature importance
    print("\nFeature Importance (Demand Model):")
    for feature, importance in zip(features, demand_model.feature_importances_):
        print(f"  {feature}: {importance:.3f}")
    
    print("\nFeature Importance (Supply Model):")
    for feature, importance in zip(features, supply_model.feature_importances_):
        print(f"  {feature}: {importance:.3f}")
    
    # Save models and metrics
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(demand_model, 'models/demand_model.pkl')
    joblib.dump(supply_model, 'models/supply_model.pkl')
    
    # Save training data sample
    data.to_csv('models/training_data_sample.csv', index=False)
    
    # Save metrics
    metrics = {
        'demand_model': demand_metrics,
        'supply_model': supply_metrics,
        'features': features,
        'training_samples': len(data),
        'districts': data['district_name'].unique().tolist()
    }
    
    with open('models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nModels saved to 'models/' directory")
    print(f"Training completed successfully!")
    
    return demand_model, supply_model, metrics

if __name__ == "__main__":
    train_models()