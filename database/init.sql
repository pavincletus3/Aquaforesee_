-- Initialize AquaForesee database with PostGIS extension

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create database user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'aquaforesee_user') THEN

      CREATE ROLE aquaforesee_user LOGIN PASSWORD 'aqua_password';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE aquaforesee TO aquaforesee_user;
GRANT ALL ON SCHEMA public TO aquaforesee_user;

-- Create tables (these will also be created by SQLAlchemy, but having them here as backup)

-- Regions table
CREATE TABLE IF NOT EXISTS regions (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    geometry GEOMETRY(POLYGON, 4326),
    population INTEGER NOT NULL,
    area_km2 FLOAT NOT NULL
);

-- Historical data table
CREATE TABLE IF NOT EXISTS historical_data (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR REFERENCES regions(id),
    year INTEGER NOT NULL,
    rainfall FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    actual_demand FLOAT NOT NULL,
    actual_supply FLOAT NOT NULL,
    stress_level VARCHAR NOT NULL
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR REFERENCES regions(id),
    scenario_id VARCHAR,
    scenario_params JSONB NOT NULL,
    predicted_values JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_historical_data_region_year ON historical_data(region_id, year);
CREATE INDEX IF NOT EXISTS idx_predictions_region ON predictions(region_id);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);

-- Create spatial index on geometry
CREATE INDEX IF NOT EXISTS idx_regions_geometry ON regions USING GIST(geometry);