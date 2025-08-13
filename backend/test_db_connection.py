#!/usr/bin/env python3
"""
Test database connection for AquaForesee
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_connection(database_url):
    """Test database connection"""
    try:
        print(f"Testing connection to: {database_url}")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test if PostGIS is available
            result = conn.execute(text("SELECT PostGIS_Version();"))
            postgis_version = result.fetchone()[0]
            print(f"PostGIS version: {postgis_version}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Test various connection strings"""
    connection_strings = [
        "postgresql://postgres:password@localhost:5432/aquaforesee",
        "postgresql://postgres@localhost:5432/aquaforesee",
        "postgresql://postgres:@localhost:5432/aquaforesee",
        "postgresql://postgres:password@127.0.0.1:5432/aquaforesee",
        "postgresql://postgres@127.0.0.1:5432/aquaforesee",
    ]
    
    print("🔧 Testing database connections...\n")
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"Test {i}:")
        if test_connection(conn_str):
            print(f"✅ Working connection string: {conn_str}")
            
            # Update the environment variable suggestion
            print(f"\n💡 Use this connection string:")
            print(f"DATABASE_URL={conn_str}")
            break
        print()
    else:
        print("❌ None of the connection strings worked.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure PostgreSQL container is running: docker-compose ps")
        print("2. Check container logs: docker-compose logs postgres")
        print("3. Try connecting directly: docker exec project-postgres-1 psql -U postgres -d aquaforesee")

if __name__ == "__main__":
    main()