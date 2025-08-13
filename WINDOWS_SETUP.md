# Windows Setup Guide for AquaForesee

If you're encountering issues with the standard installation on Windows (especially with Python 3.13), follow this guide.

## Quick Fix for Python 3.13 on Windows

### Option 1: Use the Windows Batch Script

```cmd
cd backend
install_windows.bat
```

### Option 2: Manual Installation

```cmd
cd backend

# Upgrade pip first
python -m pip install --upgrade pip wheel setuptools

# Install packages step by step
python -m pip install fastapi uvicorn[standard] pydantic python-multipart httpx

# For data science packages, use pre-compiled wheels only
python -m pip install --only-binary=all numpy pandas scikit-learn joblib

# Install database packages
python -m pip install sqlalchemy psycopg2-binary geoalchemy2 alembic

# Install security packages
python -m pip install "python-jose[cryptography]" "passlib[bcrypt]"

# Install testing
python -m pip install pytest
```

### Option 3: Use Python Installation Script

```cmd
cd backend
python install_deps.py
```

## Alternative: Use Python 3.11 or 3.12

If you continue having issues, consider using Python 3.11 or 3.12 instead of 3.13:

1. Download Python 3.11 or 3.12 from python.org
2. Create a new virtual environment:

```cmd
py -3.11 -m venv venv
# or
py -3.12 -m venv venv
```

3. Activate and install:

```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

Once dependencies are installed:

### Start Database (in project root)

```cmd
docker-compose up -d postgres
```

### Start Backend

```cmd
cd backend
python main.py
```

### Start Frontend (new terminal)

```cmd
cd frontend
npm install
npm start
```

## Troubleshooting

### Issue: "Compiler cl cannot compile programs"

This happens when trying to compile packages from source. Solutions:

1. Use `--only-binary=all` flag when installing
2. Install Visual Studio Build Tools
3. Use pre-compiled wheels

### Issue: "No module named 'sklearn'"

```cmd
pip install scikit-learn
```

### Issue: Database connection errors

Make sure Docker is running and PostgreSQL container is started:

```cmd
docker-compose ps
docker-compose logs postgres
```

### Issue: Frontend won't start

```cmd
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## Simplified Mode

If you still have issues with ML dependencies, the backend will automatically fall back to a simplified ML service that doesn't require scikit-learn. You'll see this message in the logs:

```
Using simplified ML service instead
```

The application will work fully, just with simpler prediction algorithms instead of machine learning models.

## Success Indicators

You should see:

- Backend: "Application startup completed successfully" at http://localhost:8000
- Frontend: React app at http://localhost:3000
- Database: PostgreSQL container running

## Getting Help

If you're still having issues:

1. Check the error messages carefully
2. Try the simplified installation steps above
3. Consider using a different Python version (3.11 or 3.12)
4. Make sure Docker Desktop is running for the database
