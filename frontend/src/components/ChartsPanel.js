import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import LoadingSpinner from "./LoadingSpinner";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ChartsPanel = ({ predictions, historicalData, loading }) => {
  // Line Chart: Demand vs Supply trend
  const lineChartData = {
    labels: historicalData.map((d) => d.year),
    datasets: [
      {
        label: "Demand (ML)",
        data: historicalData.map((d) => d.actual_demand),
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        tension: 0.4,
      },
      {
        label: "Supply (ML)",
        data: historicalData.map((d) => d.actual_supply),
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        tension: 0.4,
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          boxWidth: 12,
          font: { size: 11 },
        },
      },
      title: {
        display: true,
        text: "Historical Demand vs Supply",
        font: { size: 14, weight: "bold" },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { font: { size: 10 } },
      },
      x: {
        ticks: { font: { size: 10 } },
      },
    },
  };

  // Bar Chart: Top 5 most water-stressed districts
  const getTopStressedDistricts = () => {
    if (!predictions?.predictions) return [];

    return predictions.predictions
      .map((d) => ({
        name: d.district_name,
        ratio:
          d.predicted_supply > 0 ? d.predicted_demand / d.predicted_supply : 2,
      }))
      .sort((a, b) => b.ratio - a.ratio)
      .slice(0, 5);
  };

  const topStressed = getTopStressedDistricts();

  const barChartData = {
    labels: topStressed.map((d) => d.name.split(" ").slice(0, 2).join(" ")), // Shorten names
    datasets: [
      {
        label: "Stress Ratio",
        data: topStressed.map((d) => d.ratio),
        backgroundColor: topStressed.map((d) =>
          d.ratio > 1.2 ? "#ef4444" : d.ratio > 0.8 ? "#f59e0b" : "#10b981"
        ),
        borderWidth: 1,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Top 5 Water-Stressed Districts",
        font: { size: 14, weight: "bold" },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { font: { size: 10 } },
      },
      x: {
        ticks: {
          font: { size: 9 },
          maxRotation: 45,
        },
      },
    },
  };

  // Doughnut Chart: Distribution of stress levels
  const getStressDistribution = () => {
    if (!predictions?.predictions)
      return { deficit: 0, moderate: 0, surplus: 0 };

    return predictions.predictions.reduce(
      (acc, d) => {
        if (d.stress_level === "Deficit") acc.deficit++;
        else if (d.stress_level === "Moderate" || d.stress_level === "Stable")
          acc.moderate++;
        else acc.surplus++;
        return acc;
      },
      { deficit: 0, moderate: 0, surplus: 0 }
    );
  };

  const stressDistribution = getStressDistribution();

  const doughnutData = {
    labels: ["Deficit", "Moderate", "Surplus"],
    datasets: [
      {
        data: [
          stressDistribution.deficit,
          stressDistribution.moderate,
          stressDistribution.surplus,
        ],
        backgroundColor: ["#ef4444", "#f59e0b", "#10b981"],
        borderWidth: 2,
        borderColor: "#ffffff",
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 12,
          font: { size: 11 },
          padding: 15,
        },
      },
      title: {
        display: true,
        text: "Stress Level Distribution",
        font: { size: 14, weight: "bold" },
      },
    },
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="card p-4 h-48 flex items-center justify-center"
          >
            <LoadingSpinner message="Loading chart..." />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Line Chart */}
      <div className="card p-4">
        <div className="h-48">
          {historicalData.length > 0 ? (
            <Line data={lineChartData} options={lineChartOptions} />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No historical data available
            </div>
          )}
        </div>
      </div>

      {/* Bar Chart */}
      <div className="card p-4">
        <div className="h-48">
          {topStressed.length > 0 ? (
            <Bar data={barChartData} options={barChartOptions} />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No prediction data available
            </div>
          )}
        </div>
      </div>

      {/* Doughnut Chart */}
      <div className="card p-4">
        <div className="h-48">
          {predictions?.predictions ? (
            <Doughnut data={doughnutData} options={doughnutOptions} />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No prediction data available
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChartsPanel;
