# AquaForesee - Decision Support System for National Water Resource Management

A comprehensive web-based decision support tool that enables policymakers to visualize current water stress, generate forecasts, and simulate scenarios for water resource management across different regions.

## 🚀 Quick Start Guide (< 5 minutes)

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.9+

### Local Development Setup

1. **Clone and navigate to project**

```bash
git clone <repository-url>
cd aquaforesee
```

2. **Start services with Docker Compose**

```bash
docker-compose up -d
```

3. **Install frontend dependencies**

```bash
cd frontend
npm install
npm start
```

4. **Install backend dependencies**

```bash
cd ../backend
pip install -r requirements.txt
python main.py
```

5. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📋 Project Structure

```
/aquaforesee
├── /backend          # Python FastAPI server
├── /frontend         # React.js + Tailwind CSS
├── /database         # PostgreSQL setup scripts
├── /ml_models        # ML training and prediction modules
├── /data            # Sample datasets and GeoJSON files
├── docker-compose.yml
└── README.md
```

## 🏗️ Architecture Overview

- **Backend**: FastAPI with PostgreSQL/PostGIS for geospatial data
- **Frontend**: React.js with Leaflet maps and Chart.js visualizations
- **ML Models**: RandomForest for water demand/supply predictions
- **Database**: PostgreSQL with PostGIS extension for geographic data

## 📊 Key Features

- Interactive map visualization with district-level water stress indicators
- Scenario simulation with adjustable parameters (rainfall, population, temperature)
- Historical data analysis and trend visualization
- Export functionality for reports and data
- Role-based access for policymakers and researchers

## 🔧 API Endpoints

- `GET /api/regions` - List available regions
- `GET /api/baseline/{region_id}` - Baseline water forecast
- `POST /api/predict` - Scenario predictions
- `GET /api/historical/{region_id}` - Historical data

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

See individual component README files for detailed deployment instructions.

## 📄 License

MIT License - see LICENSE file for details.
