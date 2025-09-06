#!/usr/bin/env python3
"""
Quick Railway setup script for Nuvaru Platform
"""

import os
import webbrowser
from pathlib import Path

def open_services():
    """Open all required services in browser"""
    
    print("🚀 Nuvaru Platform - Quick Railway Setup")
    print("=" * 50)
    
    services = {
        "Railway": "https://railway.app/",
        "Neon DB": "https://console.neon.tech/",
        "AWS S3": "https://s3.console.aws.amazon.com/",
        "ChromaDB Cloud": "https://cloud.trychroma.com/",
        "OpenAI": "https://platform.openai.com/api-keys"
    }
    
    print("\n📋 Required Services Setup:")
    for i, (name, url) in enumerate(services.items(), 1):
        print(f"{i}. {name}: {url}")
    
    print("\n🔧 Setup Steps:")
    print("1. Set up Neon DB (database)")
    print("2. Set up AWS S3 (file storage)")
    print("3. Set up ChromaDB (vector database)")
    print("4. Get OpenAI API key")
    print("5. Deploy to Railway")
    
    # Open services in browser
    for name, url in services.items():
        response = input(f"\nOpen {name} in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open(url)
            print(f"✅ Opened {name}")

def check_railway_config():
    """Check if Railway configuration is ready"""
    
    print("\n🔍 Checking Railway Configuration...")
    
    # Check if railway.json exists
    if Path('railway.json').exists():
        print("✅ railway.json found")
    else:
        print("❌ railway.json not found")
    
    # Check if requirements.txt exists
    if Path('requirements.txt').exists():
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
    
    # Check if simple_backend.py exists
    if Path('simple_backend.py').exists():
        print("✅ simple_backend.py found")
    else:
        print("❌ simple_backend.py not found")
    
    print("\n📝 Railway Environment Variables Needed:")
    required_vars = [
        "NEON_DATABASE_URL",
        "OPENAI_API_KEY", 
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME",
        "CHROMA_AUTH_TOKEN",
        "CHROMA_API_URL",
        "SECRET_KEY"
    ]
    
    for var in required_vars:
        print(f"  - {var}")

def create_railway_commands():
    """Create Railway CLI commands"""
    
    print("\n🚀 Railway CLI Commands:")
    print("=" * 30)
    
    commands = [
        "# Install Railway CLI",
        "npm install -g @railway/cli",
        "",
        "# Login to Railway",
        "railway login",
        "",
        "# Link to your project",
        "railway link",
        "",
        "# Set environment variables",
        "railway variables set OPENAI_API_KEY=your-key",
        "railway variables set NEON_DATABASE_URL=your-db-url",
        "",
        "# Deploy",
        "railway up",
        "",
        "# View logs",
        "railway logs",
        "",
        "# Open in browser",
        "railway open"
    ]
    
    for cmd in commands:
        print(cmd)

if __name__ == "__main__":
    open_services()
    check_railway_config()
    create_railway_commands()
    
    print("\n🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Set up all services (Neon, S3, ChromaDB)")
    print("2. Get API keys and connection strings")
    print("3. Add environment variables to Railway")
    print("4. Deploy!")
    print("\nNeed help? Check DEPLOYMENT_GUIDE.md")

