from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import logging
import random
from gemini_service import GeminiService
from smart_data_generator import SmartDataGenerator

from schemas import (
    RegionResponse, 
    BaselineResponse, 
    PredictionRequest, 
    PredictionResponse,
    DistrictPrediction,
    PredictionSummary,
    HistoricalResponse
)

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

# Initialize services
gemini_service = GeminiService()
smart_generator = SmartDataGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await gemini_service.initialize()
    await smart_generator.initialize()

# Mock data
MOCK_REGIONS = [
    {
        "id": "district_1",
        "name": "Northern Plains",
        "population": 250000,
        "area_km2": 1200.5,
        "geometry": None
    },
    {
        "id": "district_2", 
        "name": "Coastal Valley",
        "population": 180000,
        "area_km2": 890.3,
        "geometry": None
    },
    {
        "id": "district_3",
        "name": "Mountain Ridge",
        "population": 120000,
        "area_km2": 1500.8,
        "geometry": None
    },
    {
        "id": "district_4",
        "name": "Central Plateau",
        "population": 300000,
        "area_km2": 980.2,
        "geometry": None
    },
    {
        "id": "district_5",
        "name": "Eastern Hills",
        "population": 95000,
        "area_km2": 1100.7,
        "geometry": None
    }
]

MOCK_HISTORICAL = [
    {"year": 2019, "rainfall": 1050.5, "temperature": 26.2, "actual_demand": 125.8, "actual_supply": 142.3, "stress_level": "Surplus"},
    {"year": 2020, "rainfall": 980.2, "temperature": 27.1, "actual_demand": 132.4, "actual_supply": 138.9, "stress_level": "Moderate"},
    {"year": 2021, "rainfall": 1120.8, "temperature": 25.8, "actual_demand": 128.9, "actual_supply": 151.2, "stress_level": "Surplus"},
    {"year": 2022, "rainfall": 890.3, "temperature": 28.4, "actual_demand": 145.2, "actual_supply": 128.7, "stress_level": "Deficit"},
    {"year": 2023, "rainfall": 1200.1, "temperature": 26.8, "actual_demand": 135.7, "actual_supply": 158.4, "stress_level": "Surplus"}
]

def calculate_demand(rainfall, temperature, population, year, month):
    """Calculate water demand using realistic formula"""
    # Base demand per capita (more realistic: 150-200 liters per person per day)
    base_demand_per_capita = 0.18  # ML per thousand people per day
    base_demand = population * base_demand_per_capita * 365  # Annual demand
    
    # Temperature effect (much more significant impact)
    temp_effect = 1.0 + max(0, (temperature - 25) * 0.15)  # 15% increase per degree above 25°C
    
    # Seasonal factor (summer months have higher demand)
    seasonal_factor = 1.0 + 0.3 * abs(6 - month) / 6  # Up to 30% seasonal variation
    
    # Year growth factor
    growth_factor = 1 + 0.03 * (year - 2020)  # 3% annual growth
    
    # Apply all factors
    demand = base_demand * temp_effect * seasonal_factor * growth_factor
    
    # Add some realistic variation
    demand *= random.uniform(0.85, 1.15)
    
    return max(demand, 10)

def calculate_supply(rainfall, temperature, population, year, month):
    """Calculate water supply using realistic formula"""
    # Base infrastructure capacity (conservative estimate)
    base_infrastructure = population * 0.12  # ML per thousand people annually
    
    # Rainfall contribution (much more sensitive to rainfall changes)
    normal_rainfall = 1000  # mm per year baseline
    rainfall_factor = max(0.3, rainfall / normal_rainfall)  # Minimum 30% of normal supply
    rainfall_supply = base_infrastructure * rainfall_factor
    
    # Temperature effect on supply (evaporation losses)
    temp_loss_factor = 1.0 - max(0, (temperature - 25) * 0.08)  # 8% loss per degree above 25°C
    
    # Infrastructure improvements over time (slower than demand growth)
    infra_factor = 1 + 0.015 * (year - 2020)  # 1.5% annual improvement
    
    # Seasonal effect (monsoon vs dry season)
    seasonal_supply_factor = 0.7 + 0.6 * (rainfall / normal_rainfall)  # More variable supply
    
    # Calculate final supply
    supply = rainfall_supply * temp_loss_factor * infra_factor * seasonal_supply_factor
    
    # Add realistic variation
    supply *= random.uniform(0.8, 1.2)
    
    return max(supply, 15)

async def generate_dynamic_historical_data(region_id: str, years: int = 5) -> List[dict]:
    """Generate realistic historical data that's consistent with the region's characteristics"""
    region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
    if not region:
        return []
    
    # Get region profile from smart generator
    region_profiles = {
        "district_1": {"base_demand": 65, "base_supply": 75, "trend": "increasing_stress"},
        "district_2": {"base_demand": 45, "base_supply": 60, "trend": "stable"},
        "district_3": {"base_demand": 35, "base_supply": 80, "trend": "improving"},
        "district_4": {"base_demand": 85, "base_supply": 70, "trend": "increasing_stress"},
        "district_5": {"base_demand": 40, "base_supply": 55, "trend": "stable"}
    }
    
    profile = region_profiles.get(region_id, region_profiles["district_1"])
    current_year = 2024
    historical_data = []
    
    for i in range(years):
        year = current_year - years + i
        
        # Generate realistic trends
        year_factor = i / (years - 1) if years > 1 else 0
        
        if profile["trend"] == "increasing_stress":
            demand_trend = 1.0 + (year_factor * 0.3)  # 30% increase over time
            supply_trend = 1.0 + (year_factor * 0.1)  # 10% increase over time
        elif profile["trend"] == "improving":
            demand_trend = 1.0 + (year_factor * 0.15)  # 15% increase
            supply_trend = 1.0 + (year_factor * 0.25)  # 25% increase
        else:  # stable
            demand_trend = 1.0 + (year_factor * 0.2)   # 20% increase
            supply_trend = 1.0 + (year_factor * 0.18)  # 18% increase
        
        # Add realistic year-to-year variation
        demand_variation = random.uniform(0.85, 1.15)
        supply_variation = random.uniform(0.8, 1.2)
        
        # Calculate values
        actual_demand = profile["base_demand"] * demand_trend * demand_variation
        actual_supply = profile["base_supply"] * supply_trend * supply_variation
        
        # Generate corresponding weather data
        if actual_supply > profile["base_supply"] * 1.1:
            rainfall = random.uniform(1100, 1400)  # Good rainfall year
            temperature = random.uniform(24, 26)
        elif actual_supply < profile["base_supply"] * 0.9:
            rainfall = random.uniform(600, 900)    # Drought year
            temperature = random.uniform(27, 30)
        else:
            rainfall = random.uniform(900, 1200)   # Normal year
            temperature = random.uniform(25, 28)
        
        # Determine stress level
        stress_ratio = actual_demand / actual_supply
        if stress_ratio > 1.1:
            stress_level = "Deficit"
        elif stress_ratio > 0.9:
            stress_level = "Moderate"
        else:
            stress_level = "Surplus"
        
        historical_data.append({
            "year": year,
            "rainfall": round(rainfall, 1),
            "temperature": round(temperature, 1),
            "actual_demand": round(actual_demand, 1),
            "actual_supply": round(actual_supply, 1),
            "stress_level": stress_level
        })
    
    return historical_data

def get_districts_for_region(region_id: str):
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

@app.get("/")
async def root():
    return {"message": "AquaForesee API is running (No Database Mode)"}

@app.post("/api/test-predict")
async def test_predict(data: dict):
    """Test endpoint to debug prediction request data"""
    logger.info(f"Raw test data received: {data}")
    for key, value in data.items():
        logger.info(f"  {key}: {value} (type: {type(value)})")
    return {"received": data}

@app.get("/api/regions", response_model=List[RegionResponse])
async def get_regions():
    """Return list of available regions"""
    return [RegionResponse(**region) for region in MOCK_REGIONS]

@app.get("/api/baseline/{region_id}", response_model=BaselineResponse)
async def get_baseline(region_id: str):
    """Fetch baseline water forecast for a region"""
    region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    districts = get_districts_for_region(region_id)
    predictions = []
    
    for district in districts:
        predicted_demand = calculate_demand(1000, 25, region["population"] / 1000, 2024, 6)
        predicted_supply = calculate_supply(1000, 25, region["population"] / 1000, 2024, 6)
        
        stress_ratio = predicted_demand / predicted_supply if predicted_supply > 0 else 2
        if stress_ratio > 1.1:  # More sensitive threshold
            stress_level = "Deficit"
        elif stress_ratio > 0.9:  # Tighter range for stable
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

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_scenario(request: PredictionRequest):
    """Accept scenario parameters and return AI-enhanced realistic predictions perfect for demos"""
    try:
        logger.info(f"Received prediction request for {len(request.region_ids)} regions: {request.region_ids}")
        
        # Validate all regions exist
        for region_id in request.region_ids:
            region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
            if not region:
                raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        

        
        # Use smart data generator for realistic results
        scenario_params = {
            "year": request.year,
            "rainfall_change_percent": request.rainfall_change_percent,
            "population_change_percent": request.population_change_percent,
            "temperature_change": request.temperature_change
        }
        
        smart_data = await smart_generator.generate_realistic_scenario(request.region_ids, scenario_params)
        
        # Convert to Pydantic models
        predictions = []
        for pred_data in smart_data["predictions"]:
            prediction = DistrictPrediction(
                district_name=pred_data["district_name"],
                predicted_demand=pred_data["predicted_demand"],
                predicted_supply=pred_data["predicted_supply"],
                stress_level=pred_data["stress_level"],
                coordinates=pred_data["coordinates"]
            )
            predictions.append(prediction)
        
        summary = PredictionSummary(
            total_districts=smart_data["summary"]["total_districts"],
            high_risk_count=smart_data["summary"]["high_risk_count"],
            average_stress_score=smart_data["summary"]["average_stress_score"]
        )
        
        logger.info(f"Generated {len(predictions)} smart predictions (AI-enhanced: {smart_data.get('ai_enhanced', False)})")
        return PredictionResponse(predictions=predictions, summary=summary)
    
    except Exception as e:
        logger.error(f"Error in predict_scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/historical/{region_id}", response_model=List[HistoricalResponse])
async def get_historical_data(region_id: str, years: int = 5):
    """Return dynamic historical water data that's consistent with current predictions"""
    region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Generate realistic historical data that leads to current conditions
    historical_data = await generate_dynamic_historical_data(region_id, years)
    return [HistoricalResponse(**data) for data in historical_data]

@app.post("/api/historical-multiple")
async def get_multiple_historical_data(region_ids: List[str], years: int = 5):
    """Return historical data for multiple regions"""
    try:
        all_historical = {}
        for region_id in region_ids:
            region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
            if region:
                historical_data = await generate_dynamic_historical_data(region_id, years)
                all_historical[region_id] = [HistoricalResponse(**data) for data in historical_data]
        
        return all_historical
    except Exception as e:
        logger.error(f"Error getting multiple historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-insights")
async def get_ai_insights(request: PredictionRequest):
    """Generate AI-powered insights for water resource scenario"""
    try:
        # Validate all regions exist
        for region_id in request.region_ids:
            region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
            if not region:
                raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Use smart data generator for consistent predictions
        scenario_params = {
            "year": request.year,
            "rainfall_change_percent": request.rainfall_change_percent,
            "population_change_percent": request.population_change_percent,
            "temperature_change": request.temperature_change
        }
        
        smart_data = await smart_generator.generate_realistic_scenario(request.region_ids, scenario_params)
        predictions = smart_data["predictions"]
        
        # Generate AI insights
        scenario_params = {
            "year": request.year,
            "rainfall_change_percent": request.rainfall_change_percent,
            "population_change_percent": request.population_change_percent,
            "temperature_change": request.temperature_change
        }
        
        # Get region names for AI context
        region_names = []
        for region_id in request.region_ids:
            region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
            if region:
                region_names.append(region["name"])
        
        region_context = ", ".join(region_names) if len(region_names) > 1 else region_names[0] if region_names else "Selected Regions"
        
        insights = await gemini_service.generate_water_insights(
            predictions, scenario_params, region_context
        )
        
        policy_recommendations = await gemini_service.generate_policy_recommendations(
            predictions, scenario_params
        )
        
        scenario_summary = await gemini_service.generate_scenario_summary(
            predictions, scenario_params
        )
        
        return {
            "insights": insights,
            "policy_recommendations": policy_recommendations,
            "scenario_summary": scenario_summary,
            "predictions_count": len(predictions),
            "high_risk_count": len([p for p in predictions if p["stress_level"] == "Deficit"])
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI insights: {str(e)}")

@app.post("/api/key-insights")
async def get_key_insights(request: PredictionRequest):
    """Generate AI-powered key insights for the scenario"""
    try:
        # Validate all regions exist
        for region_id in request.region_ids:
            region = next((r for r in MOCK_REGIONS if r["id"] == region_id), None)
            if not region:
                raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Use smart data generator for predictions
        scenario_params = {
            "year": request.year,
            "rainfall_change_percent": request.rainfall_change_percent,
            "population_change_percent": request.population_change_percent,
            "temperature_change": request.temperature_change
        }
        
        smart_data = await smart_generator.generate_realistic_scenario(request.region_ids, scenario_params)
        predictions = smart_data["predictions"]
        
        # Generate AI-powered key insights
        if gemini_service.is_initialized:
            try:
                prompt = f"""
                As a water resource analyst, provide 3-4 key insights for this scenario:
                
                SCENARIO: {request.year} with {request.rainfall_change_percent}% rainfall, +{request.population_change_percent}% population, +{request.temperature_change}°C temperature
                
                RESULTS: {smart_data["summary"]["high_risk_count"]} out of {smart_data["summary"]["total_districts"]} districts in deficit
                
                Provide insights as bullet points focusing on:
                - Most critical finding
                - Surprising or counterintuitive result
                - Actionable recommendation
                - Future trend prediction
                
                Keep each insight to 1-2 sentences, practical and specific.
                """
                
                response = gemini_service.model.generate_content(prompt)
                ai_insights = response.text
            except Exception as e:
                logger.error(f"AI insights generation failed: {e}")
                ai_insights = None
        else:
            ai_insights = None
        
        # Fallback to smart insights if AI fails
        if not ai_insights:
            ai_insights = generate_smart_insights(scenario_params, smart_data["summary"])
        
        return {
            "key_insights": ai_insights,
            "scenario_summary": f"Analysis of {smart_data['summary']['total_districts']} districts shows {smart_data['summary']['high_risk_count']} at high risk",
            "ai_generated": gemini_service.is_initialized and ai_insights
        }
        
    except Exception as e:
        logger.error(f"Error generating key insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

def generate_smart_insights(scenario_params: Dict, summary: Dict) -> str:
    """Generate smart insights without AI"""
    insights = []
    
    rainfall = scenario_params['rainfall_change_percent']
    temp = scenario_params['temperature_change']
    pop = scenario_params['population_change_percent']
    high_risk = summary['high_risk_count']
    total = summary['total_districts']
    
    # Critical finding
    if high_risk > total * 0.5:
        insights.append(f"• CRITICAL: {high_risk} out of {total} districts face water deficits, indicating a regional water crisis requiring immediate intervention.")
    elif high_risk == 0:
        insights.append(f"• POSITIVE: All {total} districts maintain adequate water supply, suggesting effective resource management under current conditions.")
    else:
        insights.append(f"• MODERATE RISK: {high_risk} districts show water stress, requiring targeted interventions while maintaining regional stability.")
    
    # Scenario-specific insight
    if rainfall > 30:
        insights.append(f"• RAINFALL IMPACT: The {rainfall}% increase in rainfall significantly improves water availability, demonstrating the critical importance of precipitation patterns.")
    elif rainfall < -20:
        insights.append(f"• DROUGHT CONCERN: The {rainfall}% rainfall reduction creates substantial supply challenges, highlighting vulnerability to climate variability.")
    
    # Temperature effect
    if temp > 5:
        insights.append(f"• TEMPERATURE STRESS: The {temp}°C temperature increase substantially raises water demand through increased evaporation and cooling needs.")
    
    # Population pressure
    if pop > 50:
        insights.append(f"• GROWTH PRESSURE: {pop}% population growth significantly strains water infrastructure, requiring capacity expansion and efficiency improvements.")
    
    return "\n".join(insights[:4])  # Limit to 4 insights

@app.get("/api/ai-status")
async def get_ai_status():
    """Check if AI service is available"""
    return {
        "ai_enabled": gemini_service.is_initialized,
        "service": "Gemini AI" if gemini_service.is_initialized else "Disabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)