"""
Smart Data Generator using Gemini AI for realistic water resource scenarios
Perfect for hackathon demonstrations with believable but impressive results
"""

import random
import logging
from typing import Dict, List, Tuple, Union
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SmartDataGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.is_initialized = False
        
        # Cache for generated scenarios to ensure consistency
        self.scenario_cache = {}
        
        # Base realistic parameters for different regions
        self.region_profiles = {
            "district_1": {  # Northern Plains - Agricultural
                "base_demand_factor": 1.2,
                "rainfall_sensitivity": 0.8,
                "temp_sensitivity": 1.1,
                "description": "Agricultural region with high irrigation needs"
            },
            "district_2": {  # Coastal Valley - Moderate
                "base_demand_factor": 0.9,
                "rainfall_sensitivity": 0.6,
                "temp_sensitivity": 0.8,
                "description": "Coastal region with moderate water stress"
            },
            "district_3": {  # Mountain Ridge - Low demand
                "base_demand_factor": 0.7,
                "rainfall_sensitivity": 1.2,
                "temp_sensitivity": 0.6,
                "description": "Mountainous region with good water sources"
            },
            "district_4": {  # Central Plateau - Urban
                "base_demand_factor": 1.4,
                "rainfall_sensitivity": 0.5,
                "temp_sensitivity": 1.3,
                "description": "Urban region with high population density"
            },
            "district_5": {  # Eastern Hills - Rural
                "base_demand_factor": 0.8,
                "rainfall_sensitivity": 1.0,
                "temp_sensitivity": 0.9,
                "description": "Rural hilly region with seasonal variations"
            },
            
        }
    
    async def initialize(self):
        """Initialize the Gemini AI service"""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.is_initialized = True
                logger.info("Smart Data Generator with Gemini AI initialized")
            else:
                logger.info("Smart Data Generator initialized without AI (using smart algorithms)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            return True  # Continue without AI
    
    def generate_scenario_key(self, region_id: str, scenario_params: Dict) -> str:
        """Generate a unique key for scenario caching"""
        return f"{region_id}_{scenario_params['year']}_{scenario_params['rainfall_change_percent']}_{scenario_params['population_change_percent']}_{scenario_params['temperature_change']}"
    
    async def generate_realistic_scenario(self, region_ids: Union[str, List[str]], scenario_params: Dict) -> Dict:
        """Generate realistic water scenario data using AI insights for multiple regions"""
        # Handle single region for backward compatibility
        if isinstance(region_ids, str):
            region_ids = [region_ids]
        
        scenario_key = self.generate_scenario_key("_".join(region_ids), scenario_params)
        
        # Check cache first
        if scenario_key in self.scenario_cache:
            return self.scenario_cache[scenario_key]
        
        # Generate predictions for all selected regions
        all_predictions = []
        
        for region_id in region_ids:
            # Get AI-enhanced parameters if available
            ai_factors = await self._get_ai_scenario_factors(region_id, scenario_params)
            
            # Generate district-level data for this region
            districts = self._get_districts_for_region(region_id)
            
            for i, district in enumerate(districts):
                district_data = self._generate_district_data(
                    region_id, district, scenario_params, ai_factors, i
                )
                all_predictions.append(district_data)
        
        # Calculate summary with smart distribution
        summary = self._calculate_smart_summary(all_predictions, scenario_params)
        
        result = {
            "predictions": all_predictions,
            "summary": summary,
            "ai_enhanced": self.is_initialized
        }
        
        # Cache the result
        self.scenario_cache[scenario_key] = result
        return result
    
    async def _get_ai_scenario_factors(self, region_id: str, scenario_params: Dict) -> Dict:
        """Get AI-enhanced factors for more realistic scenarios"""
        if not self.is_initialized:
            return self._get_smart_factors(scenario_params)
        
        try:
            region_desc = self.region_profiles[region_id]["description"]
            
            prompt = f"""
            As a water resource expert, analyze this realistic water scenario for {region_desc}:
            
            SCENARIO DETAILS:
            - Region: {region_desc}
            - Year: {scenario_params['year']}
            - Rainfall Change: {scenario_params['rainfall_change_percent']}%
            - Population Growth: +{scenario_params['population_change_percent']}%
            - Temperature Change: +{scenario_params['temperature_change']}°C
            
            ANALYSIS RULES:
            - +50% rainfall should significantly IMPROVE water supply (reduce stress)
            - +3°C temperature increases demand but not catastrophically
            - Population growth increases demand proportionally
            - Consider regional characteristics and climate adaptation
            - Be realistic: not every scenario should be a crisis
            
            Provide realistic impact factors as numbers only:
            demand_multiplier: [0.7-1.8]
            supply_multiplier: [0.4-2.2]
            stress_reduction_bonus: [0.0-0.3]
            district_variation: [0.1-0.3]
            
            IMPORTANT: High rainfall (+30% or more) should create surplus conditions in most cases.
            """
            
            response = self.model.generate_content(prompt)
            factors = self._parse_ai_factors(response.text)
            return factors
            
        except Exception as e:
            logger.error(f"AI factor generation failed: {e}")
            return self._get_smart_factors(scenario_params)
    
    def _parse_ai_factors(self, ai_response: str) -> Dict:
        """Parse AI response into usable factors"""
        try:
            factors = {}
            lines = ai_response.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    # Extract number from value (handle brackets and text)
                    import re
                    numbers = re.findall(r'[\d.]+', value.strip())
                    if numbers:
                        value = float(numbers[0])
                        factors[key] = max(0.1, min(3.0, value))
            
            # Ensure all required factors exist with better defaults
            return {
                'demand_multiplier': factors.get('demand_multiplier', 1.0),
                'supply_multiplier': factors.get('supply_multiplier', 1.0),
                'stress_reduction_bonus': factors.get('stress_reduction_bonus', 0.0),
                'district_variation': factors.get('district_variation', 0.2)
            }
        except Exception as e:
            logger.error(f"Failed to parse AI factors: {e}")
            return self._get_smart_factors({})
    
    def _get_smart_factors(self, scenario_params: Dict) -> Dict:
        """Generate smart factors without AI - much more realistic"""
        rainfall_change = scenario_params.get('rainfall_change_percent', 0)
        temp_change = scenario_params.get('temperature_change', 0)
        pop_change = scenario_params.get('population_change_percent', 0)
        
        # Much more realistic demand calculation
        # Population has direct impact, temperature has moderate impact
        demand_multiplier = 1.0 + (pop_change * 0.01) + (temp_change * 0.08)
        
        # Supply is VERY sensitive to rainfall, moderately affected by temperature
        supply_multiplier = 1.0 + (rainfall_change * 0.025) - (temp_change * 0.05)
        
        # Bonus for very high rainfall scenarios
        stress_reduction_bonus = 0.0
        if rainfall_change > 30:
            stress_reduction_bonus = 0.2  # Significant stress reduction
        elif rainfall_change > 15:
            stress_reduction_bonus = 0.1  # Moderate stress reduction
        
        # More variation in extreme scenarios
        district_variation = 0.15 + (abs(rainfall_change) * 0.002)
        
        return {
            'demand_multiplier': max(0.7, min(1.8, demand_multiplier)),
            'supply_multiplier': max(0.4, min(2.5, supply_multiplier)),
            'stress_reduction_bonus': max(0.0, min(0.3, stress_reduction_bonus)),
            'district_variation': max(0.1, min(0.3, district_variation))
        }
    
    def _generate_district_data(self, region_id: str, district: Dict, scenario_params: Dict, ai_factors: Dict, district_index: int) -> Dict:
        """Generate realistic district-level water data"""
        profile = self.region_profiles.get(region_id, self.region_profiles["district_1"])
        
        # Base calculations with regional variations
        base_population = 40 + (district_index * 25)  # Varied district sizes
        population_factor = base_population * (1 + scenario_params['population_change_percent'] / 100)
        
        # More realistic demand calculation
        base_demand = population_factor * 0.16 * profile['base_demand_factor']
        temp_effect = 1.0 + (scenario_params['temperature_change'] * profile['temp_sensitivity'] * 0.06)
        demand = base_demand * temp_effect * ai_factors['demand_multiplier']
        
        # Much more realistic supply calculation
        base_supply = population_factor * 0.14  # Slightly higher base supply
        
        # Rainfall has major impact on supply
        rainfall_effect = 1.0 + (scenario_params['rainfall_change_percent'] / 100 * profile['rainfall_sensitivity'] * 1.5)
        
        # Temperature reduces supply through evaporation
        temp_loss = 1.0 - (scenario_params['temperature_change'] * 0.03)
        
        supply = base_supply * rainfall_effect * temp_loss * ai_factors['supply_multiplier']
        
        # Add district-specific variation
        variation = ai_factors['district_variation']
        demand *= random.uniform(1 - variation, 1 + variation)
        supply *= random.uniform(1 - variation, 1 + variation)
        
        # Ensure realistic minimum values
        demand = max(demand, 20)
        supply = max(supply, 15)
        
        # Calculate stress level with bonus for good conditions
        stress_ratio = demand / supply
        
        # Apply stress reduction bonus for good rainfall
        if ai_factors.get('stress_reduction_bonus', 0) > 0:
            stress_ratio *= (1 - ai_factors['stress_reduction_bonus'])
        
        # More realistic thresholds
        if stress_ratio > 1.2:
            stress_level = "Deficit"
        elif stress_ratio > 0.85:
            stress_level = "Stable"
        else:
            stress_level = "Surplus"
        
        return {
            "district_name": district["name"],
            "predicted_demand": round(demand, 1),
            "predicted_supply": round(supply, 1),
            "stress_level": stress_level,
            "coordinates": district["coordinates"]
        }
    
    def _calculate_smart_summary(self, predictions: List[Dict], scenario_params: Dict) -> Dict:
        """Calculate summary with realistic distribution"""
        total_districts = len(predictions)
        deficit_count = sum(1 for p in predictions if p["stress_level"] == "Deficit")
        surplus_count = sum(1 for p in predictions if p["stress_level"] == "Surplus")
        
        # Apply realistic scenario logic
        rainfall_change = scenario_params['rainfall_change_percent']
        temp_change = scenario_params['temperature_change']
        pop_change = scenario_params['population_change_percent']
        
        # Very good conditions (high rainfall, low temp increase)
        if rainfall_change > 30 and temp_change < 4:
            # Should have mostly surplus
            target_surplus = max(int(total_districts * 0.7), 1)
            current_surplus = surplus_count
            
            if current_surplus < target_surplus:
                # Convert some stable/deficit to surplus
                for p in predictions:
                    if current_surplus >= target_surplus:
                        break
                    if p["stress_level"] in ["Stable", "Deficit"]:
                        p["stress_level"] = "Surplus"
                        current_surplus += 1
        
        # Severe drought conditions (low rainfall, high temp)
        elif rainfall_change < -30 or (rainfall_change < -15 and temp_change > 6):
            # Should have some deficits
            target_deficit = max(int(total_districts * 0.4), 1)
            current_deficit = deficit_count
            
            if current_deficit < target_deficit:
                # Convert some stable/surplus to deficit
                for p in predictions:
                    if current_deficit >= target_deficit:
                        break
                    if p["stress_level"] in ["Stable", "Surplus"]:
                        p["stress_level"] = "Deficit"
                        current_deficit += 1
        
        # Recalculate after adjustments
        deficit_count = sum(1 for p in predictions if p["stress_level"] == "Deficit")
        avg_stress = sum(p["predicted_demand"] / p["predicted_supply"] 
                        for p in predictions if p["predicted_supply"] > 0) / total_districts
        
        return {
            "total_districts": total_districts,
            "high_risk_count": deficit_count,
            "average_stress_score": round(avg_stress, 2)
        }
    
    def _get_districts_for_region(self, region_id: str) -> List[Dict]:
        """Get districts for a region"""
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