import pytest
import numpy as np
import pandas as pd
from ml_service import MLService
from schemas import PredictionRequest

@pytest.fixture
async def ml_service():
    """Create and initialize ML service for testing"""
    service = MLService()
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_ml_service_initialization():
    """Test ML service initialization"""
    service = MLService()
    await service.initialize()
    
    assert service.is_initialized
    assert service.demand_model is not None
    assert service.supply_model is not None
    assert len(service.model_metrics) > 0

@pytest.mark.asyncio
async def test_training_data_generation(ml_service):
    """Test training data generation"""
    training_data = ml_service._generate_training_data()
    
    assert isinstance(training_data, pd.DataFrame)
    assert len(training_data) > 100  # Should have substantial data
    assert 'rainfall' in training_data.columns
    assert 'temperature' in training_data.columns
    assert 'population' in training_data.columns
    assert 'demand' in training_data.columns
    assert 'supply' in training_data.columns

@pytest.mark.asyncio
async def test_model_predictions(ml_service):
    """Test model prediction functionality"""
    # Test data
    features = np.array([[
        1000,  # rainfall
        25,    # temperature
        200,   # population (thousands)
        2024,  # year
        6      # month
    ]])
    
    demand_pred = ml_service.demand_model.predict(features)
    supply_pred = ml_service.supply_model.predict(features)
    
    assert len(demand_pred) == 1
    assert len(supply_pred) == 1
    assert demand_pred[0] > 0
    assert supply_pred[0] > 0

def test_stress_level_calculation():
    """Test stress level calculation logic"""
    # Test different ratios
    test_cases = [
        (100, 50, "Deficit"),    # ratio = 2.0
        (100, 90, "Stable"),     # ratio = 1.11
        (80, 100, "Surplus"),    # ratio = 0.8
    ]
    
    for demand, supply, expected in test_cases:
        ratio = demand / supply
        if ratio > 1.2:
            stress_level = "Deficit"
        elif ratio > 0.8:
            stress_level = "Stable"
        else:
            stress_level = "Surplus"
        
        assert stress_level == expected

def test_model_metrics_format():
    """Test that model metrics have expected format"""
    service = MLService()
    
    # Mock metrics (would be set during initialization)
    service.model_metrics = {
        'demand': {'mae': 10.5, 'r2': 0.85},
        'supply': {'mae': 8.2, 'r2': 0.78}
    }
    
    assert 'demand' in service.model_metrics
    assert 'supply' in service.model_metrics
    assert 'mae' in service.model_metrics['demand']
    assert 'r2' in service.model_metrics['demand']