import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for loading states
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error("API Error:", error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error("Network Error:", error.request);
    } else {
      // Something else happened
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get all regions
  getRegions: async () => {
    const response = await api.get("/api/regions");
    return response.data;
  },

  // Get baseline forecast for a region
  getBaseline: async (regionId) => {
    const response = await api.get(`/api/baseline/${regionId}`);
    return response.data;
  },

  // Generate scenario predictions
  predictScenario: async (scenarioData) => {
    const response = await api.post("/api/predict", scenarioData);
    return response.data;
  },

  // Get historical data for a region
  getHistoricalData: async (regionId, years = 5) => {
    const response = await api.get(
      `/api/historical/${regionId}?years=${years}`
    );
    return response.data;
  },

  // Get AI-powered insights
  getAIInsights: async (scenarioData) => {
    const response = await api.post("/api/ai-insights", scenarioData);
    return response.data;
  },

  // Check AI service status
  getAIStatus: async () => {
    const response = await api.get("/api/ai-status");
    return response.data;
  },

  // Get AI-powered key insights
  getKeyInsights: async (scenarioData) => {
    const response = await api.post("/api/key-insights", scenarioData);
    return response.data;
  },
};

export default api;
