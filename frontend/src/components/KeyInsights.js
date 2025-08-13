import React from "react";
import { Lightbulb, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";
import LoadingSpinner from "./LoadingSpinner";

const KeyInsights = ({ insights, loading }) => {
  // Insights are now passed as props from Dashboard
  // Generated only when "Run Scenario" is clicked

  const getInsightIcon = (insight) => {
    if (insight.includes("CRITICAL") || insight.includes("CRISIS")) {
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    } else if (insight.includes("POSITIVE") || insight.includes("EFFECTIVE")) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else {
      return <TrendingUp className="w-4 h-4 text-blue-500" />;
    }
  };

  const formatInsights = (insightsText) => {
    if (!insightsText) return [];

    return insightsText
      .split("\n")
      .filter((line) => line.trim().startsWith("•"))
      .map((line) => line.trim().substring(1).trim());
  };

  if (loading) {
    return (
      <div className="card p-4">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-900">Key Insights</h3>
        </div>
        <div className="py-4">
          <LoadingSpinner message="Analyzing scenario..." />
        </div>
      </div>
    );
  }

  return (
    <div className="card p-4">
      <div className="flex items-center space-x-2 mb-4">
        <Lightbulb className="w-5 h-5 text-yellow-500" />
        <h3 className="text-lg font-semibold text-gray-900">Key Insights</h3>
        {insights?.ai_generated && (
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
            AI-Powered
          </span>
        )}
      </div>

      {insights ? (
        <div className="space-y-3">
          {/* Scenario Summary */}
          {insights.scenario_summary && (
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-700 font-medium">
                {insights.scenario_summary}
              </p>
            </div>
          )}

          {/* Key Insights */}
          <div className="space-y-2">
            {formatInsights(insights.key_insights).map((insight, index) => (
              <div
                key={index}
                className="flex items-start space-x-3 p-3 bg-white border border-gray-200 rounded-lg"
              >
                {getInsightIcon(insight)}
                <p className="text-sm text-gray-800 leading-relaxed flex-1">
                  {insight}
                </p>
              </div>
            ))}
          </div>

          {/* Insight Quality Indicator */}
          <div className="text-xs text-gray-500 text-center pt-2 border-t">
            {insights.ai_generated
              ? "Insights generated using advanced AI analysis"
              : "Insights generated using smart algorithms"}
          </div>
        </div>
      ) : (
        <div className="text-center py-6 text-gray-500">
          <Lightbulb className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm">
            Run a scenario to see key insights about water resource conditions
          </p>
        </div>
      )}
    </div>
  );
};

export default KeyInsights;
