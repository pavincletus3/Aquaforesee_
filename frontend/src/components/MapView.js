import React, { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import LoadingSpinner from "./LoadingSpinner";

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom icons for different stress levels
const createCustomIcon = (stressLevel) => {
  const colors = {
    Deficit: "#ef4444",
    Stable: "#f59e0b",
    Moderate: "#f59e0b",
    Surplus: "#10b981",
  };

  return L.divIcon({
    className: "custom-marker",
    html: `
      <div style="
        background-color: ${colors[stressLevel] || "#6b7280"};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

// Legend component
const MapLegend = () => {
  const map = useMap();
  const legendRef = useRef();

  useEffect(() => {
    if (legendRef.current) return;

    const legend = L.control({ position: "bottomright" });

    legend.onAdd = () => {
      const div = L.DomUtil.create("div", "legend");
      div.style.cssText = `
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-size: 12px;
        line-height: 18px;
      `;

      div.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">Water Stress Levels</div>
        <div><span style="display: inline-block; width: 12px; height: 12px; background: #ef4444; border-radius: 50%; margin-right: 8px;"></span>Deficit</div>
        <div><span style="display: inline-block; width: 12px; height: 12px; background: #f59e0b; border-radius: 50%; margin-right: 8px;"></span>Moderate</div>
        <div><span style="display: inline-block; width: 12px; height: 12px; background: #10b981; border-radius: 50%; margin-right: 8px;"></span>Surplus</div>
      `;

      return div;
    };

    legend.addTo(map);
    legendRef.current = legend;

    return () => {
      if (legendRef.current) {
        map.removeControl(legendRef.current);
        legendRef.current = null;
      }
    };
  }, [map]);

  return null;
};

const MapView = ({ predictions, selectedRegions, loading }) => {
  const defaultCenter = [28.0, 77.0]; // Default to India coordinates
  const defaultZoom = 6;

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner message="Updating map..." />
      </div>
    );
  }

  return (
    <div className="h-full relative">
      <div className="absolute top-4 left-4 z-10 bg-white px-3 py-2 rounded-lg shadow-md">
        <h3 className="font-semibold text-gray-900">Water Stress Map</h3>
        <p className="text-sm text-gray-600">
          {predictions
            ? `${predictions.predictions?.length || 0} districts analyzed`
            : "Select a region to view data"}
        </p>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        className="h-full w-full rounded-lg"
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        <MapLegend />

        {predictions?.predictions?.map((district, index) => (
          <Marker
            key={`${district.district_name}-${index}`}
            position={district.coordinates}
            icon={createCustomIcon(district.stress_level)}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {district.district_name}
                </h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Demand:</span>
                    <span className="font-medium">
                      {district.predicted_demand.toFixed(1)} ML
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Supply:</span>
                    <span className="font-medium">
                      {district.predicted_supply.toFixed(1)} ML
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span
                      className={`font-medium ${
                        district.stress_level === "Deficit"
                          ? "text-red-600"
                          : district.stress_level === "Moderate"
                          ? "text-yellow-600"
                          : "text-green-600"
                      }`}
                    >
                      {district.stress_level}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ratio:</span>
                    <span className="font-medium">
                      {(
                        district.predicted_demand / district.predicted_supply
                      ).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;
