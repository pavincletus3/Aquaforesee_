import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";
import MapView from "./MapView";
import ChartsPanel from "./ChartsPanel";
import SummaryPanel from "./SummaryPanel";
import LoadingSpinner from "./LoadingSpinner";
import AIInsights from "./AIInsights";
import KeyInsights from "./KeyInsights";
import { apiService } from "../services/api";
import toast from "react-hot-toast";

const Dashboard = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // State management
  const [regions, setRegions] = useState([]);
  const [selectedRegions, setSelectedRegions] = useState([]);
  const [scenarioParams, setScenarioParams] = useState({
    year: 2024,
    rainfall_change_percent: 0,
    population_change_percent: 0,
    temperature_change: 0,
  });
  const [predictions, setPredictions] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [keyInsights, setKeyInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setInitialLoading(true);
        const regionsData = await apiService.getRegions();
        setRegions(regionsData);

        // Select first region by default
        if (regionsData.length > 0) {
          setSelectedRegions([regionsData[0].id]);
          await loadRegionData([regionsData[0].id]);
        }
      } catch (error) {
        console.error("Failed to load initial data:", error);
        toast.error("Failed to load regions data");
      } finally {
        setInitialLoading(false);
      }
    };

    if (isAuthenticated) {
      loadInitialData();
    }
  }, [isAuthenticated]);

  const loadRegionData = async (regionIds) => {
    try {
      if (regionIds.length === 0) return;

      // Load baseline for first region (for initial display)
      const baseline = await apiService.getBaseline(regionIds[0]);
      setPredictions(baseline);

      // Load and combine historical data from all selected regions
      const historicalPromises = regionIds.map((regionId) =>
        apiService.getHistoricalData(regionId)
      );

      const allHistoricalData = await Promise.all(historicalPromises);

      // Combine and average historical data across regions
      const combinedHistorical = combineHistoricalData(allHistoricalData);
      setHistoricalData(combinedHistorical);
    } catch (error) {
      console.error("Failed to load region data:", error);
      toast.error("Failed to load region data");
    }
  };

  const combineHistoricalData = (allHistoricalData) => {
    if (allHistoricalData.length === 0) return [];
    if (allHistoricalData.length === 1) return allHistoricalData[0];

    // Get years from first dataset
    const years = allHistoricalData[0].map((d) => d.year);

    return years
      .map((year) => {
        const yearData = allHistoricalData
          .map((regionData) => regionData.find((d) => d.year === year))
          .filter(Boolean);

        if (yearData.length === 0) return null;

        // Average the values across regions
        const avgDemand =
          yearData.reduce((sum, d) => sum + d.actual_demand, 0) /
          yearData.length;
        const avgSupply =
          yearData.reduce((sum, d) => sum + d.actual_supply, 0) /
          yearData.length;
        const avgRainfall =
          yearData.reduce((sum, d) => sum + d.rainfall, 0) / yearData.length;
        const avgTemp =
          yearData.reduce((sum, d) => sum + d.temperature, 0) / yearData.length;

        // Determine overall stress level
        const stressRatio = avgDemand / avgSupply;
        let stress_level = "Surplus";
        if (stressRatio > 1.1) stress_level = "Deficit";
        else if (stressRatio > 0.9) stress_level = "Moderate";

        return {
          year,
          actual_demand: Math.round(avgDemand * 10) / 10,
          actual_supply: Math.round(avgSupply * 10) / 10,
          rainfall: Math.round(avgRainfall * 10) / 10,
          temperature: Math.round(avgTemp * 10) / 10,
          stress_level,
        };
      })
      .filter(Boolean);
  };

  const handleRegionChange = async (regionIds) => {
    setSelectedRegions(regionIds);
    if (regionIds.length > 0) {
      await loadRegionData(regionIds); // Load data for all selected regions
    }
  };

  const handleScenarioChange = (params) => {
    setScenarioParams((prev) => ({ ...prev, ...params }));
  };

  const runScenario = async () => {
    if (selectedRegions.length === 0) {
      toast.error("Please select at least one region");
      return;
    }

    try {
      setLoading(true);
      const scenarioData = {
        region_ids: selectedRegions, // Send all selected regions
        ...scenarioParams,
      };

      // Run scenario prediction and key insights in parallel
      const [predictionResult, insightsResult] = await Promise.all([
        apiService.predictScenario(scenarioData),
        apiService.getKeyInsights(scenarioData).catch((error) => {
          console.warn("Key insights failed:", error);
          return null; // Don't fail the whole process if insights fail
        }),
      ]);

      setPredictions(predictionResult);
      setKeyInsights(insightsResult);

      toast.success("Scenario analysis completed");
    } catch (error) {
      console.error("Failed to run scenario:", error);
      toast.error("Failed to run scenario analysis");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (initialLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner size="large" message="Loading AquaForesee..." />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <Header />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          regions={regions}
          selectedRegions={selectedRegions}
          onRegionChange={handleRegionChange}
          scenarioParams={scenarioParams}
          onScenarioChange={handleScenarioChange}
          onRunScenario={runScenario}
          loading={loading}
        />

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Map Area */}
          <div className="flex-1 p-4">
            <div className="h-full card p-4">
              <MapView
                predictions={predictions}
                selectedRegions={selectedRegions}
                loading={loading}
              />
            </div>
          </div>

          {/* Right Panel */}
          <div className="w-80 p-4 overflow-y-auto max-h-full">
            <div className="space-y-4">
              <KeyInsights insights={keyInsights} loading={loading} />
              <ChartsPanel
                predictions={predictions}
                historicalData={historicalData}
                loading={loading}
              />
              <AIInsights
                scenarioParams={scenarioParams}
                selectedRegions={selectedRegions}
                predictions={predictions}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Panel */}
      <div className="h-48 border-t bg-white">
        <SummaryPanel
          predictions={predictions}
          scenarioParams={scenarioParams}
          loading={loading}
        />
      </div>
    </div>
  );
};

export default Dashboard;
