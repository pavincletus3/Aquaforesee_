from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RegionResponse(BaseModel):
    id: str
    name: str
    population: int
    area_km2: float
    geometry: Optional[str] = None

class BaselineResponse(BaseModel):
    region_id: str
    predictions: List[Dict[str, Any]]
    summary: Dict[str, Any]

class PredictionRequest(BaseModel):
    region_ids: List[str]  # Changed to accept multiple regions
    year: int = Field(..., ge=2024, le=2030)
    rainfall_change_percent: float = Field(..., ge=-50.0, le=50.0)
    population_change_percent: float = Field(..., ge=0.0, le=100.0)
    temperature_change: float = Field(..., ge=-5.0, le=10.0)

class DistrictPrediction(BaseModel):
    district_name: str
    predicted_demand: float
    predicted_supply: float
    stress_level: str  # Deficit|Stable|Surplus
    coordinates: List[float]  # [lat, lng]

class PredictionSummary(BaseModel):
    total_districts: int
    high_risk_count: int
    average_stress_score: float
    model_accuracy: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    predictions: List[DistrictPrediction]
    summary: PredictionSummary

class HistoricalResponse(BaseModel):
    year: int
    rainfall: float
    temperature: float
    actual_demand: float
    actual_supply: float
    stress_level: str

class ErrorResponse(BaseModel):
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)