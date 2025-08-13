@echo off
echo Installing AquaForesee Backend Dependencies for Windows...

REM Upgrade pip first
python -m pip install --upgrade pip wheel setuptools

REM Install packages one by one to handle any issues
echo Installing FastAPI and core web packages...
python -m pip install fastapi uvicorn[standard] pydantic python-multipart httpx

echo Installing data science packages (this might take a while)...
python -m pip install --only-binary=all numpy pandas scikit-learn joblib

echo Installing database packages...
python -m pip install sqlalchemy psycopg2-binary geoalchemy2 alembic

echo Installing security packages...
python -m pip install "python-jose[cryptography]" "passlib[bcrypt]"

echo Installing testing packages...
python -m pip install pytest

echo.
echo ✅ Installation complete!
echo You can now run: python main.py
pause