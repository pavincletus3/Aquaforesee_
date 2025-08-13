import React, { useState } from "react";
import {
  Brain,
  Lightbulb,
  AlertTriangle,
  TrendingUp,
  FileText,
} from "lucide-react";
import { apiService } from "../services/api";
import toast from "react-hot-toast";
import LoadingSpinner from "./LoadingSpinner";

const AIInsights = ({ scenarioParams, selectedRegions, predictions }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiEnabled, setAiEnabled] = useState(true);

  const generateInsights = async () => {
    if (selectedRegions.length === 0) {
      toast.error("Please select a region first");
      return;
    }

    try {
      setLoading(true);
      const scenarioData = {
        region_ids: selectedRegions, // Send all selected regions
        ...scenarioParams,
      };

      const result = await apiService.getAIInsights(scenarioData);
      setInsights(result);
      toast.success("AI insights generated successfully!");
    } catch (error) {
      console.error("Failed to generate AI insights:", error);
      if (error.response?.status === 500) {
        setAiEnabled(false);
        toast.error("AI service is currently unavailable");
      } else {
        toast.error("Failed to generate AI insights");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!aiEnabled) {
    return (
      <div className="card p-6">
        <div className="text-center text-gray-500">
          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            AI Insights Unavailable
          </h3>
          <p className="text-sm">AI-powered insights are currently disabled.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Brain className="w-6 h-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI-Powered Insights
          </h3>
        </div>
        <button
          onClick={generateInsights}
          disabled={loading || selectedRegions.length === 0}
          className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="spinner mr-2"></div>
              Analyzing...
            </>
          ) : (
            <>
              <Lightbulb className="w-4 h-4 mr-2" />
              Generate Insights
            </>
          )}
        </button>
      </div>

      {loading && (
        <div className="py-8">
          <LoadingSpinner message="AI is analyzing your water scenario..." />
        </div>
      )}

      {insights && !loading && (
        <div className="space-y-6">
          {/* Scenario Summary */}
          {insights.scenario_summary && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900 mb-2">
                    Executive Summary
                  </h4>
                  <p className="text-sm text-blue-800 leading-relaxed">
                    {insights.scenario_summary}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Key Insights */}
          {insights.insights && (
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-green-900 mb-2">
                    Water Resource Analysis
                  </h4>
                  <div className="text-sm text-green-800 whitespace-pre-line leading-relaxed">
                    {insights.insights}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Policy Recommendations */}
          {insights.policy_recommendations && (
            <div className="bg-amber-50 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-amber-900 mb-2">
                    Policy Recommendations
                  </h4>
                  <div className="text-sm text-amber-800 whitespace-pre-line leading-relaxed">
                    {insights.policy_recommendations}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {insights.predictions_count || 0}
              </div>
              <div className="text-sm text-gray-600">Districts Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {insights.high_risk_count || 0}
              </div>
              <div className="text-sm text-gray-600">High Risk Districts</div>
            </div>
          </div>
        </div>
      )}

      {!insights && !loading && (
        <div className="text-center py-8 text-gray-500">
          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-sm">
            Click "Generate Insights" to get AI-powered analysis of your water
            scenario
          </p>
        </div>
      )}
    </div>
  );
};

export default AIInsights;
