from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from geoalchemy2 import Geometry

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/aquaforesee")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models import Region, HistoricalData, Prediction
    Base.metadata.create_all(bind=engine)
    
    # Seed initial data if tables are empty
    db = SessionLocal()
    try:
        if db.query(Region).count() == 0:
            seed_data(db)
    finally:
        db.close()

def seed_data(db):
    """Seed database with initial sample data"""
    from models import Region, HistoricalData
    import json
    
    # Sample regions data
    regions_data = [
        {
            "id": "district_1",
            "name": "Northern Plains",
            "population": 250000,
            "area_km2": 1200.5,
            "geometry": "POLYGON((77.0 28.0, 78.0 28.0, 78.0 29.0, 77.0 29.0, 77.0 28.0))"
        },
        {
            "id": "district_2", 
            "name": "Coastal Valley",
            "population": 180000,
            "area_km2": 890.3,
            "geometry": "POLYGON((76.0 27.0, 77.0 27.0, 77.0 28.0, 76.0 28.0, 76.0 27.0))"
        },
        {
            "id": "district_3",
            "name": "Mountain Ridge",
            "population": 120000,
            "area_km2": 1500.8,
            "geometry": "POLYGON((78.0 29.0, 79.0 29.0, 79.0 30.0, 78.0 30.0, 78.0 29.0))"
        },
        {
            "id": "district_4",
            "name": "Central Plateau",
            "population": 300000,
            "area_km2": 980.2,
            "geometry": "POLYGON((77.0 27.0, 78.0 27.0, 78.0 28.0, 77.0 28.0, 77.0 27.0))"
        },
        {
            "id": "district_5",
            "name": "Eastern Hills",
            "population": 95000,
            "area_km2": 1100.7,
            "geometry": "POLYGON((79.0 28.0, 80.0 28.0, 80.0 29.0, 79.0 29.0, 79.0 28.0))"
        }
    ]
    
    # Create regions
    for region_data in regions_data:
        region = Region(**region_data)
        db.add(region)
    
    # Create historical data for each region
    import random
    for region_data in regions_data:
        for year in range(2019, 2024):
            # Generate realistic historical data with correlations
            base_rainfall = random.uniform(800, 1200)
            base_temp = random.uniform(22, 28)
            population_factor = region_data["population"] / 100000
            
            demand = population_factor * random.uniform(80, 120) + (base_temp - 25) * 5
            supply = base_rainfall * 0.1 + random.uniform(-20, 20)
            
            stress_ratio = demand / supply if supply > 0 else 2
            if stress_ratio > 1.2:
                stress_level = "Deficit"
            elif stress_ratio > 0.8:
                stress_level = "Moderate"
            else:
                stress_level = "Surplus"
            
            historical = HistoricalData(
                region_id=region_data["id"],
                year=year,
                rainfall=base_rainfall,
                temperature=base_temp,
                actual_demand=demand,
                actual_supply=supply,
                stress_level=stress_level
            )
            db.add(historical)
    
    db.commit()