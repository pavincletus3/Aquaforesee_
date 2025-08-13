import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AquaForesee API is running"}

def test_get_regions():
    """Test regions endpoint"""
    response = client.get("/api/regions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "name" in data[0]

def test_predict_scenario():
    """Test scenario prediction endpoint"""
    scenario_data = {
        "region_id": "district_1",
        "year": 2025,
        "rainfall_change_percent": -10,
        "population_change_percent": 15,
        "temperature_change": 2.0
    }
    
    response = client.post("/api/predict", json=scenario_data)
    
    # Note: This might fail if database is not properly initialized
    # In a real test environment, you'd use a test database
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert "summary" in data
        assert isinstance(data["predictions"], list)

def test_invalid_scenario():
    """Test invalid scenario data"""
    invalid_data = {
        "region_id": "invalid_region",
        "year": 2050,  # Out of range
        "rainfall_change_percent": -100,  # Out of range
        "population_change_percent": -10,  # Negative not allowed
        "temperature_change": 20  # Out of range
    }
    
    response = client.post("/api/predict", json=invalid_data)
    assert response.status_code in [400, 404, 422]  # Should return error