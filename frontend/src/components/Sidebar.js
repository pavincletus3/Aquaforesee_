import React from "react";
import { Play, Settings, MapPin } from "lucide-react";

const Sidebar = ({
  regions,
  selectedRegions,
  onRegionChange,
  scenarioParams,
  onScenarioChange,
  onRunScenario,
  loading,
}) => {
  const handleRegionToggle = (regionId) => {
    const isSelected = selectedRegions.includes(regionId);
    if (isSelected) {
      onRegionChange(selectedRegions.filter((id) => id !== regionId));
    } else {
      onRegionChange([...selectedRegions, regionId]);
    }
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
      <div className="space-y-6">
        {/* Region Selection */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <MapPin className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Select Regions
            </h3>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto">
            {regions.map((region) => (
              <label
                key={region.id}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedRegions.includes(region.id)}
                  onChange={() => handleRegionToggle(region.id)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    {region.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    Pop: {(region.population / 1000).toFixed(0)}K • Area:{" "}
                    {region.area_km2.toFixed(0)} km²
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Scenario Parameters */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Settings className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Scenario Parameters
            </h3>
          </div>

          <div className="space-y-4">
            {/* Year Slider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Year: {scenarioParams.year}
              </label>
              <input
                type="range"
                min="2024"
                max="2030"
                value={scenarioParams.year}
                onChange={(e) =>
                  onScenarioChange({ year: parseInt(e.target.value) })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>2024</span>
                <span>2030</span>
              </div>
            </div>

            {/* Rainfall Change */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rainfall Change:{" "}
                {scenarioParams.rainfall_change_percent > 0 ? "+" : ""}
                {scenarioParams.rainfall_change_percent}%
              </label>
              <input
                type="range"
                min="-50"
                max="50"
                value={scenarioParams.rainfall_change_percent}
                onChange={(e) =>
                  onScenarioChange({
                    rainfall_change_percent: parseInt(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>-50%</span>
                <span>+50%</span>
              </div>
            </div>

            {/* Population Change */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Population Change: +{scenarioParams.population_change_percent}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={scenarioParams.population_change_percent}
                onChange={(e) =>
                  onScenarioChange({
                    population_change_percent: parseInt(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0%</span>
                <span>+100%</span>
              </div>
            </div>

            {/* Temperature Change */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature Change:{" "}
                {scenarioParams.temperature_change > 0 ? "+" : ""}
                {scenarioParams.temperature_change}°C
              </label>
              <input
                type="range"
                min="-5"
                max="10"
                step="0.5"
                value={scenarioParams.temperature_change}
                onChange={(e) =>
                  onScenarioChange({
                    temperature_change: parseFloat(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>-5°C</span>
                <span>+10°C</span>
              </div>
            </div>
          </div>
        </div>

        {/* Run Scenario Button */}
        <button
          onClick={onRunScenario}
          disabled={loading || selectedRegions.length === 0}
          className="w-full btn-primary py-3 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="spinner"></div>
              <span>Running Analysis...</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Run Scenario</span>
            </>
          )}
        </button>

        {/* Quick Info */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Quick Tips</h4>
          <ul className="text-xs text-blue-800 space-y-1">
            <li>• Select multiple regions to compare</li>
            <li>• Adjust parameters to simulate scenarios</li>
            <li>• Click districts on map for details</li>
            <li>• Export reports from summary panel</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
