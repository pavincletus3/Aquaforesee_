from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
from database import Base

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geometry = Column(Geometry('POLYGON'), nullable=True)
    population = Column(Integer, nullable=False)
    area_km2 = Column(Float, nullable=False)
    
    # Relationships
    historical_data = relationship("HistoricalData", back_populates="region")
    predictions = relationship("Prediction", back_populates="region")

class HistoricalData(Base):
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String, ForeignKey("regions.id"), nullable=False)
    year = Column(Integer, nullable=False)
    rainfall = Column(Float, nullable=False)  # mm
    temperature = Column(Float, nullable=False)  # celsius
    actual_demand = Column(Float, nullable=False)  # ML
    actual_supply = Column(Float, nullable=False)  # ML
    stress_level = Column(String, nullable=False)  # Deficit|Moderate|Surplus
    
    # Relationships
    region = relationship("Region", back_populates="historical_data")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String, ForeignKey("regions.id"), nullable=False)
    scenario_id = Column(String, nullable=True)
    scenario_params = Column(JSON, nullable=False)
    predicted_values = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    region = relationship("Region", back_populates="predictions")