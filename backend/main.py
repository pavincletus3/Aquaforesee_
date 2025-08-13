from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db, init_db
from models import Region, HistoricalData, Prediction
from schemas import (
    RegionResponse, 
    BaselineResponse, 
    PredictionRequest, 
    PredictionResponse,
    HistoricalResponse
)
try:
    from ml_service import MLService
    ML_SERVICE_TYPE = "full"
except ImportError as e:
    logger.warning(f"Could not import full ML service: {e}")
    logger.info("Using simplified ML service instead")
    from ml_service_simple import SimpleMLService as MLService
    ML_SERVICE_TYPE = "simple"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AquaForesee API",
    description="Decision Support System for National Water Resource Management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML service
ml_service = MLService()

@app.on_event("startup")
async def startup_event():
    """Initialize database and ML models on startup"""
    try:
        init_db()
        await ml_service.initialize()
        logger.info(f"Application startup completed successfully using {ML_SERVICE_TYPE} ML service")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "AquaForesee API is running"}

@app.get("/api/regions", response_model=List[RegionResponse])
async def get_regions(db: Session = Depends(get_db)):
    """Return list of available regions from database"""
    try:
        regions = db.query(Region).all()
        return [
            RegionResponse(
                id=region.id,
                name=region.name,
                population=region.population,
                area_km2=region.area_km2,
                geometry=region.geometry
            )
            for region in regions
        ]
    except Exception as e:
        logger.error(f"Error fetching regions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch regions")

@app.get("/api/baseline/{region_id}", response_model=BaselineResponse)
async def get_baseline(region_id: str, db: Session = Depends(get_db)):
    """Fetch baseline water forecast for a region"""
    try:
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        
        # Get latest historical data for baseline
        latest_data = db.query(HistoricalData)\
            .filter(HistoricalData.region_id == region_id)\
            .order_by(HistoricalData.year.desc())\
            .first()
        
        if not latest_data:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        baseline = await ml_service.get_baseline_prediction(region_id, latest_data)
        return baseline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching baseline for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch baseline")

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_scenario(request: PredictionRequest, db: Session = Depends(get_db)):
    """Accept scenario parameters and return updated predictions"""
    try:
        # Validate region exists
        region = db.query(Region).filter(Region.id == request.region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        
        # Generate predictions using ML service
        predictions = await ml_service.predict_scenario(request, db)
        
        # Store prediction in database
        prediction_record = Prediction(
            region_id=request.region_id,
            scenario_params=request.dict(),
            predicted_values=predictions.dict()
        )
        db.add(prediction_record)
        db.commit()
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")

@app.get("/api/historical/{region_id}", response_model=List[HistoricalResponse])
async def get_historical_data(
    region_id: str, 
    years: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    """Return historical water data for charts"""
    try:
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        
        historical_data = db.query(HistoricalData)\
            .filter(HistoricalData.region_id == region_id)\
            .order_by(HistoricalData.year.desc())\
            .limit(years)\
            .all()
        
        return [
            HistoricalResponse(
                year=data.year,
                rainfall=data.rainfall,
                temperature=data.temperature,
                actual_demand=data.actual_demand,
                actual_supply=data.actual_supply,
                stress_level=data.stress_level
            )
            for data in historical_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data for region {region_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)