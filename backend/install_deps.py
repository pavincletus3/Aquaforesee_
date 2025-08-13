#!/usr/bin/env python3
"""
Install dependencies for AquaForesee backend with Python 3.13 compatibility
"""

import subprocess
import sys
import os

def run_pip_install(packages):
    """Install packages using pip"""
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    return True

def main():
    """Main installation function"""
    print("🔧 Installing AquaForesee backend dependencies...")
    
    # Core packages first
    core_packages = [
        "pip --upgrade",
        "wheel",
        "setuptools",
    ]
    
    # Install core packages
    for package in core_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + package.split())
        except subprocess.CalledProcessError:
            pass
    
    # Essential packages in order
    essential_packages = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "python-multipart",
        "httpx",
    ]
    
    # Data science packages (might need pre-compiled wheels)
    data_packages = [
        "numpy",
        "pandas", 
        "scikit-learn",
        "joblib",
    ]
    
    # Database packages
    db_packages = [
        "sqlalchemy",
        "psycopg2-binary",
        "geoalchemy2",
        "alembic",
    ]
    
    # Security packages
    security_packages = [
        "python-jose[cryptography]",
        "passlib[bcrypt]",
    ]
    
    # Testing packages
    test_packages = [
        "pytest",
    ]
    
    # Install in groups
    package_groups = [
        ("Essential packages", essential_packages),
        ("Data science packages", data_packages),
        ("Database packages", db_packages),
        ("Security packages", security_packages),
        ("Testing packages", test_packages),
    ]
    
    for group_name, packages in package_groups:
        print(f"\n📦 Installing {group_name}...")
        if not run_pip_install(packages):
            print(f"❌ Failed to install {group_name}")
            print("💡 Try installing manually or use a different Python version")
            return False
    
    print("\n✅ All dependencies installed successfully!")
    print("🚀 You can now run: python main.py")
    return True

if __name__ == "__main__":
    main()