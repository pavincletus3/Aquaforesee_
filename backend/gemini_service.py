"""
Gemini AI Service for AquaForesee
Provides AI-powered insights and recommendations for water resource management
"""

import os
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Gemini AI service"""
        try:
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not found. AI insights will be disabled.")
                return False
                
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_initialized = True
            logger.info("Gemini AI service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            return False
    
    async def generate_water_insights(self, predictions: List[Dict], scenario_params: Dict, region_name: str = None) -> Optional[str]:
        """Generate AI-powered insights for water resource predictions"""
        if not self.is_initialized:
            return None
            
        try:
            # Prepare data summary for AI analysis
            total_districts = len(predictions)
            deficit_districts = [p for p in predictions if p.get("stress_level") == "Deficit"]
            surplus_districts = [p for p in predictions if p.get("stress_level") == "Surplus"]
            
            avg_demand = sum(p.get("predicted_demand", 0) for p in predictions) / total_districts if total_districts > 0 else 0
            avg_supply = sum(p.get("predicted_supply", 0) for p in predictions) / total_districts if total_districts > 0 else 0
            
            # Create prompt for Gemini
            prompt = f"""
            As a water resource management expert, analyze the following water stress scenario and provide actionable insights:

            SCENARIO PARAMETERS:
            - Region: {region_name or "Selected Region"}
            - Target Year: {scenario_params.get('year', 2024)}
            - Rainfall Change: {scenario_params.get('rainfall_change_percent', 0)}%
            - Population Change: +{scenario_params.get('population_change_percent', 0)}%
            - Temperature Change: {scenario_params.get('temperature_change', 0)}°C

            CURRENT PREDICTIONS:
            - Total Districts: {total_districts}
            - Districts in Deficit: {len(deficit_districts)}
            - Districts with Surplus: {len(surplus_districts)}
            - Average Water Demand: {avg_demand:.1f} ML
            - Average Water Supply: {avg_supply:.1f} ML
            - Overall Stress Ratio: {avg_demand/avg_supply:.2f if avg_supply > 0 else 'N/A'}

            CRITICAL DISTRICTS:
            {chr(10).join([f"- {d.get('district_name', 'Unknown')}: {d.get('stress_level', 'Unknown')} (Demand: {d.get('predicted_demand', 0):.1f} ML, Supply: {d.get('predicted_supply', 0):.1f} ML)" for d in deficit_districts[:5]])}

            Please provide:
            1. Risk Assessment (2-3 sentences)
            2. Key Concerns (3-4 bullet points)
            3. Recommended Actions (4-5 specific recommendations)
            4. Long-term Strategy (2-3 sentences)

            Keep the response concise, actionable, and focused on practical water management solutions.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating water insights: {e}")
            return None
    
    async def generate_policy_recommendations(self, predictions: List[Dict], scenario_params: Dict) -> Optional[str]:
        """Generate policy recommendations based on water stress analysis"""
        if not self.is_initialized:
            return None
            
        try:
            high_risk_districts = [p for p in predictions if p.get("stress_level") == "Deficit"]
            
            prompt = f"""
            As a water policy advisor, provide policy recommendations for the following water crisis scenario:

            SCENARIO OVERVIEW:
            - {len(high_risk_districts)} out of {len(predictions)} districts are in water deficit
            - Climate scenario: {scenario_params.get('rainfall_change_percent', 0)}% rainfall change, +{scenario_params.get('temperature_change', 0)}°C temperature increase
            - Population growth: +{scenario_params.get('population_change_percent', 0)}%

            HIGH-RISK DISTRICTS:
            {chr(10).join([f"- {d.get('district_name', 'Unknown')}: Demand {d.get('predicted_demand', 0):.1f} ML vs Supply {d.get('predicted_supply', 0):.1f} ML" for d in high_risk_districts[:3]])}

            Provide specific policy recommendations in these categories:
            1. IMMEDIATE ACTIONS (0-6 months)
            2. SHORT-TERM POLICIES (6 months - 2 years)
            3. LONG-TERM STRATEGIES (2-10 years)
            4. REGULATORY MEASURES
            5. INVESTMENT PRIORITIES

            Focus on practical, implementable policies with clear timelines and expected outcomes.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating policy recommendations: {e}")
            return None
    
    async def generate_scenario_summary(self, predictions: List[Dict], scenario_params: Dict) -> Optional[str]:
        """Generate a concise summary of the scenario analysis"""
        if not self.is_initialized:
            return None
            
        try:
            prompt = f"""
            Summarize this water resource scenario in 2-3 sentences for policymakers:

            SCENARIO: Year {scenario_params.get('year', 2024)} with {scenario_params.get('rainfall_change_percent', 0)}% rainfall change, +{scenario_params.get('population_change_percent', 0)}% population growth, +{scenario_params.get('temperature_change', 0)}°C temperature increase.

            RESULTS: {len([p for p in predictions if p.get("stress_level") == "Deficit"])} districts in deficit, {len([p for p in predictions if p.get("stress_level") == "Surplus"])} districts with surplus out of {len(predictions)} total districts.

            Provide a clear, executive-level summary focusing on the key implications and urgency level.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating scenario summary: {e}")
            return None