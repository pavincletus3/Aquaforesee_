import React from "react";
import {
  Download,
  AlertTriangle,
  TrendingUp,
  Droplets,
  Users,
} from "lucide-react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import toast from "react-hot-toast";

const SummaryPanel = ({ predictions, scenarioParams, loading }) => {
  const generatePDFReport = async () => {
    try {
      toast.loading("Generating PDF report...");

      // Create PDF
      const pdf = new jsPDF();
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      // Title
      pdf.setFontSize(20);
      pdf.text("AquaForesee - Water Resource Analysis Report", 20, 30);

      // Date
      pdf.setFontSize(12);
      pdf.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 45);

      // Scenario Parameters
      pdf.setFontSize(16);
      pdf.text("Scenario Parameters:", 20, 65);
      pdf.setFontSize(12);
      pdf.text(`Target Year: ${scenarioParams.year}`, 25, 80);
      pdf.text(
        `Rainfall Change: ${scenarioParams.rainfall_change_percent}%`,
        25,
        90
      );
      pdf.text(
        `Population Change: ${scenarioParams.population_change_percent}%`,
        25,
        100
      );
      pdf.text(
        `Temperature Change: ${scenarioParams.temperature_change}°C`,
        25,
        110
      );

      // Summary Statistics
      if (predictions?.summary) {
        pdf.setFontSize(16);
        pdf.text("Summary Statistics:", 20, 130);
        pdf.setFontSize(12);
        pdf.text(
          `Total Districts Analyzed: ${predictions.summary.total_districts}`,
          25,
          145
        );
        pdf.text(
          `High Risk Districts: ${predictions.summary.high_risk_count}`,
          25,
          155
        );
        pdf.text(
          `Average Stress Score: ${predictions.summary.average_stress_score}`,
          25,
          165
        );
      }

      // District Details
      if (predictions?.predictions) {
        pdf.setFontSize(16);
        pdf.text("District Analysis:", 20, 185);

        let yPos = 200;
        predictions.predictions.forEach((district, index) => {
          if (yPos > pageHeight - 40) {
            pdf.addPage();
            yPos = 30;
          }

          pdf.setFontSize(12);
          pdf.text(`${index + 1}. ${district.district_name}`, 25, yPos);
          pdf.text(
            `   Demand: ${district.predicted_demand.toFixed(1)} ML`,
            30,
            yPos + 10
          );
          pdf.text(
            `   Supply: ${district.predicted_supply.toFixed(1)} ML`,
            30,
            yPos + 20
          );
          pdf.text(`   Status: ${district.stress_level}`, 30, yPos + 30);

          yPos += 45;
        });
      }

      // Save PDF
      pdf.save("aquaforesee-report.pdf");
      toast.dismiss();
      toast.success("PDF report downloaded successfully");
    } catch (error) {
      toast.dismiss();
      toast.error("Failed to generate PDF report");
      console.error("PDF generation error:", error);
    }
  };

  const exportData = () => {
    if (!predictions?.predictions) {
      toast.error("No data available to export");
      return;
    }

    try {
      const csvData = [
        [
          "District Name",
          "Predicted Demand (ML)",
          "Predicted Supply (ML)",
          "Stress Level",
          "Coordinates",
        ],
        ...predictions.predictions.map((d) => [
          d.district_name,
          d.predicted_demand.toFixed(2),
          d.predicted_supply.toFixed(2),
          d.stress_level,
          `"${d.coordinates.join(", ")}"`,
        ]),
      ];

      const csvContent = csvData.map((row) => row.join(",")).join("\n");
      const blob = new Blob([csvContent], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "aquaforesee-data.csv";
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success("Data exported successfully");
    } catch (error) {
      toast.error("Failed to export data");
      console.error("Export error:", error);
    }
  };

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Scenario Summary & Export
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={exportData}
            disabled={!predictions?.predictions || loading}
            className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
          <button
            onClick={generatePDFReport}
            disabled={!predictions?.predictions || loading}
            className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-2" />
            Download PDF Report
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Districts */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <Droplets className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">
              Total Districts
            </span>
          </div>
          <div className="text-2xl font-bold text-blue-900 mt-1">
            {predictions?.summary?.total_districts || 0}
          </div>
        </div>

        {/* High Risk */}
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="text-sm font-medium text-red-900">High Risk</span>
          </div>
          <div className="text-2xl font-bold text-red-900 mt-1">
            {predictions?.summary?.high_risk_count || 0}
          </div>
        </div>

        {/* Average Stress */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-900">
              Avg Stress
            </span>
          </div>
          <div className="text-2xl font-bold text-yellow-900 mt-1">
            {predictions?.summary?.average_stress_score?.toFixed(2) || "0.00"}
          </div>
        </div>

        {/* Model Accuracy */}
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Model R²</span>
          </div>
          <div className="text-2xl font-bold text-green-900 mt-1">
            {predictions?.summary?.model_accuracy?.demand?.r2?.toFixed(2) ||
              "N/A"}
          </div>
        </div>
      </div>

      {/* Current Scenario Parameters */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">
          Current Scenario Parameters
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Target Year:</span>
            <span className="ml-2 font-medium">{scenarioParams.year}</span>
          </div>
          <div>
            <span className="text-gray-600">Rainfall Change:</span>
            <span className="ml-2 font-medium">
              {scenarioParams.rainfall_change_percent > 0 ? "+" : ""}
              {scenarioParams.rainfall_change_percent}%
            </span>
          </div>
          <div>
            <span className="text-gray-600">Population Change:</span>
            <span className="ml-2 font-medium">
              +{scenarioParams.population_change_percent}%
            </span>
          </div>
          <div>
            <span className="text-gray-600">Temperature Change:</span>
            <span className="ml-2 font-medium">
              {scenarioParams.temperature_change > 0 ? "+" : ""}
              {scenarioParams.temperature_change}°C
            </span>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      {predictions?.predictions && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Key Insights</h4>
          <div className="text-sm text-blue-800 space-y-1">
            <p>
              • {predictions.summary.high_risk_count} out of{" "}
              {predictions.summary.total_districts} districts are at high risk
              of water deficit
            </p>
            <p>
              • Average stress ratio is{" "}
              {predictions.summary.average_stress_score.toFixed(2)}
              {predictions.summary.average_stress_score > 1
                ? " (demand exceeds supply)"
                : " (supply meets demand)"}
            </p>
            {scenarioParams.rainfall_change_percent < 0 && (
              <p>
                • Reduced rainfall scenario increases water stress across all
                districts
              </p>
            )}
            {scenarioParams.population_change_percent > 20 && (
              <p>• High population growth significantly impacts water demand</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryPanel;
