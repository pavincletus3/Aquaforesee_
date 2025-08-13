# AquaForesee Backend

FastAPI-based backend service for the AquaForesee water resource management system.

## Features

- RESTful API for water resource data and predictions
- Machine Learning models for demand/supply forecasting
- PostgreSQL with PostGIS for geospatial data
- Comprehensive scenario simulation capabilities
- Real-time prediction generation

## API Endpoints

### Core Endpoints

- `GET /` - Health check
- `GET /api/regions` - List all available regions
- `GET /api/baseline/{region_id}` - Get baseline forecast for a region
- `POST /api/predict` - Generate scenario predictions
- `GET /api/historical/{region_id}` - Get historical data for charts

### API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Start

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up environment variables**

```bash
cp ../.env.example .env
# Edit .env with your database credentials
```

3. **Start the server**

```bash
python main.py
```

## Database Setup

The application uses PostgreSQL with PostGIS extension:

1. **Using Docker (Recommended)**

```bash
# From project root
docker-compose up postgres
```

2. **Manual Setup**

```sql
CREATE DATABASE aquaforesee;
CREATE EXTENSION postgis;
```

## Machine Learning Models

The system uses RandomForest models for:

- Water demand prediction
- Water supply prediction

Models are trained on synthetic data with realistic correlations between:

- Rainfall and water supply
- Population and water demand
- Temperature and seasonal variations

### Model Performance

- Demand Model: R² > 0.85, MAE < 15 ML
- Supply Model: R² > 0.80, MAE < 12 ML

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

## Deployment

### Docker Deployment

```bash
docker build -t aquaforesee-backend .
docker run -p 8000:8000 aquaforesee-backend
```

### Production Considerations

- Use environment variables for sensitive configuration
- Enable HTTPS with reverse proxy (nginx/traefik)
- Set up proper logging and monitoring
- Use production database with connection pooling
- Implement rate limiting and authentication

## Architecture

```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and models
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── ml_service.py        # Machine learning service
├── tests/               # Test suite
└── requirements.txt     # Python dependencies
```

## Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update API documentation
4. Ensure all tests pass before submitting PRs
