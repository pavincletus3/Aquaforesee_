#!/usr/bin/env python3
"""
AquaForesee Setup Script
Automated setup for the complete AquaForesee project
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_requirements():
    """Check if required tools are installed"""
    requirements = {
        'python': 'python --version',
        'node': 'node --version', 
        'npm': 'npm --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        result = run_command(command, check=False)
        if result.returncode != 0:
            missing.append(tool)
        else:
            print(f"✓ {tool} is installed")
    
    if missing:
        print(f"\n❌ Missing required tools: {', '.join(missing)}")
        print("\nPlease install the missing tools and run setup again.")
        sys.exit(1)
    
    print("\n✅ All required tools are installed!")

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    # Create virtual environment
    if not os.path.exists('backend/venv'):
        run_command('python -m venv venv', cwd='backend')
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip'
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    run_command(f'{pip_cmd} install --upgrade pip', cwd='backend')
    run_command(f'{pip_cmd} install -r requirements.txt', cwd='backend')
    
    print("✅ Backend dependencies installed!")

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    # Install npm dependencies
    run_command('npm install', cwd='frontend')
    
    print("✅ Frontend dependencies installed!")

def setup_database():
    """Set up the database using Docker"""
    print("\n🔧 Setting up database...")
    
    # Start PostgreSQL with Docker Compose
    run_command('docker-compose up -d postgres')
    
    print("✅ Database container started!")
    print("⏳ Waiting for database to be ready...")
    
    # Wait for database to be ready
    import time
    time.sleep(10)
    
    print("✅ Database should be ready!")

def train_ml_models():
    """Train the machine learning models"""
    print("\n🔧 Training ML models...")
    
    # Run model training
    if os.name == 'nt':  # Windows
        python_cmd = 'backend\\venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_cmd = 'backend/venv/bin/python'
    
    run_command(f'{python_cmd} ml_models/train_model.py')
    
    print("✅ ML models trained and saved!")

def create_env_files():
    """Create environment files from examples"""
    print("\n🔧 Creating environment files...")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from .env.example")
        else:
            print("⚠️  .env.example not found, skipping .env creation")
    
    # Create frontend .env file
    frontend_env_content = """REACT_APP_API_URL=http://localhost:8000
"""
    
    frontend_env_path = Path('frontend/.env')
    if not frontend_env_path.exists():
        frontend_env_path.write_text(frontend_env_content)
        print("✅ Created frontend/.env file")

def verify_setup():
    """Verify that the setup was successful"""
    print("\n🔍 Verifying setup...")
    
    checks = [
        ('Backend virtual environment', 'backend/venv'),
        ('Frontend node_modules', 'frontend/node_modules'),
        ('ML models directory', 'ml_models/models'),
        ('Environment file', '.env'),
        ('Frontend environment file', 'frontend/.env')
    ]
    
    all_good = True
    for name, path in checks:
        if os.path.exists(path):
            print(f"✅ {name}: Found")
        else:
            print(f"❌ {name}: Missing")
            all_good = False
    
    return all_good

def print_next_steps():
    """Print instructions for running the application"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. Start the backend server:")
    if os.name == 'nt':  # Windows
        print("   cd backend")
        print("   venv\\Scripts\\python main.py")
    else:  # Unix/Linux/Mac
        print("   cd backend")
        print("   venv/bin/python main.py")
    
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm start")
    
    print("\n3. Open your browser and navigate to:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n4. Login with any name and role to access the dashboard")
    
    print("\n🔧 Useful Commands:")
    print("   - Stop database: docker-compose down")
    print("   - View logs: docker-compose logs")
    print("   - Restart services: docker-compose restart")
    
    print("\n📚 Documentation:")
    print("   - Project README: ./README.md")
    print("   - Backend README: ./backend/README.md")
    print("   - Frontend README: ./frontend/README.md")
    print("   - ML Models README: ./ml_models/README.md")

def main():
    """Main setup function"""
    print("🚀 AquaForesee Setup Script")
    print("="*40)
    
    try:
        # Check requirements
        check_requirements()
        
        # Create environment files
        create_env_files()
        
        # Setup components
        setup_backend()
        setup_frontend()
        setup_database()
        train_ml_models()
        
        # Verify setup
        if verify_setup():
            print_next_steps()
        else:
            print("\n❌ Setup verification failed. Please check the errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()