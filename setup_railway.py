#!/usr/bin/env python3
"""
Railway deployment setup script for Nuvaru Platform
"""

import os
import sys
from pathlib import Path

def setup_railway_environment():
    """Setup environment variables for Railway deployment"""
    
    print("🚀 Setting up Railway deployment environment...")
    
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Please create one from env.example")
        return False
    
    # Required environment variables for Railway
    required_vars = [
        'NEON_DATABASE_URL',
        'OPENAI_API_KEY',
        'S3_BUCKET_NAME',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Railway project settings or .env file")
        return False
    
    print("✅ All required environment variables are set")
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    
    # Check if simple_backend.py exists
    if not Path('simple_backend.py').exists():
        print("❌ simple_backend.py not found")
        return False
    
    print("✅ simple_backend.py found")
    
    print("\n🎉 Railway setup complete!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repo to Railway")
    print("3. Set environment variables in Railway dashboard")
    print("4. Deploy!")
    
    return True

def create_railway_env_template():
    """Create a Railway-specific environment template"""
    
    template = """# Railway Environment Variables Template
# Copy these to your Railway project settings

# Database
NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# AI
OPENAI_API_KEY=sk-proj-your-openai-api-key

# File Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Vector Database
CHROMA_AUTH_TOKEN=your-chroma-auth-token
CHROMA_API_URL=https://your-instance.chromadb.com

# Security
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production

# CORS
BACKEND_CORS_ORIGINS=https://your-frontend.vercel.app
"""
    
    with open('railway.env.template', 'w') as f:
        f.write(template)
    
    print("✅ Created railway.env.template")

if __name__ == "__main__":
    print("🚀 Nuvaru Platform - Railway Setup")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Setup Railway environment
    success = setup_railway_environment()
    
    if success:
        create_railway_env_template()
        print("\n📋 Railway deployment checklist:")
        print("□ Code pushed to GitHub")
        print("□ Railway project created")
        print("□ Environment variables set")
        print("□ Database (Neon) configured")
        print("□ File storage (S3) configured")
        print("□ Vector DB (ChromaDB) configured")
        print("□ Frontend deployed (Vercel)")
        print("□ Domain configured")
    else:
        print("\n❌ Setup failed. Please fix the issues above.")
        sys.exit(1)

