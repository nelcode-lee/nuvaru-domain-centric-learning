#!/usr/bin/env python3
"""
Quick setup script for external services required by Nuvaru Platform
"""

import webbrowser
import os
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_service(name, url, description, env_vars):
    """Print service information"""
    print(f"\n🔧 {name}")
    print(f"   URL: {url}")
    print(f"   Description: {description}")
    print(f"   Environment Variables: {', '.join(env_vars)}")
    
    response = input(f"   Open {name} in browser? (y/n): ").lower()
    if response == 'y':
        webbrowser.open(url)
        return True
    return False

def create_service_guide():
    """Create a detailed service setup guide"""
    guide = """
# 🔧 External Services Setup Guide

## 1. Neon DB (Database)
- **URL**: https://console.neon.tech/
- **Steps**:
  1. Create a new account
  2. Create a new project
  3. Copy the connection string
  4. Add to Railway: `NEON_DATABASE_URL=postgresql://...`

## 2. AWS S3 (File Storage)
- **URL**: https://s3.console.aws.amazon.com/
- **Steps**:
  1. Create a new S3 bucket (e.g., `nuvaru-documents-prod`)
  2. Create an IAM user with S3 permissions
  3. Generate access keys
  4. Add to Railway:
     - `AWS_ACCESS_KEY_ID=your-key`
     - `AWS_SECRET_ACCESS_KEY=your-secret`
     - `S3_BUCKET_NAME=your-bucket`
     - `AWS_REGION=us-east-1`

## 3. ChromaDB Cloud (Vector Database)
- **URL**: https://cloud.trychroma.com/
- **Steps**:
  1. Create a new account
  2. Create a new instance
  3. Get API URL and auth token
  4. Add to Railway:
     - `CHROMA_AUTH_TOKEN=your-token`
     - `CHROMA_API_URL=https://your-instance.chromadb.com`

## 4. OpenAI (AI Services)
- **URL**: https://platform.openai.com/api-keys
- **Steps**:
  1. Create a new API key
  2. Add to Railway: `OPENAI_API_KEY=sk-proj-...`

## 5. Railway (Hosting)
- **URL**: https://railway.app/
- **Steps**:
  1. Connect your GitHub repository
  2. Create a new project
  3. Add all environment variables
  4. Deploy!

## Cost Estimation
- **Neon DB**: Free tier available, ~$0-19/month
- **AWS S3**: 5GB free, ~$0.023/GB
- **ChromaDB Cloud**: Free tier available, ~$0-25/month
- **OpenAI**: Pay per use, ~$0.002/1K tokens
- **Railway**: $5-20/month
- **Total**: ~$5-65/month
"""
    
    with open("SERVICE_SETUP_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Service setup guide created: SERVICE_SETUP_GUIDE.md")

def main():
    """Main setup function"""
    print_header("Nuvaru Platform - External Services Setup")
    
    services = [
        {
            "name": "Neon DB (Database)",
            "url": "https://console.neon.tech/",
            "description": "Create a new project and get the connection string",
            "env_vars": ["NEON_DATABASE_URL"]
        },
        {
            "name": "AWS S3 (File Storage)",
            "url": "https://s3.console.aws.amazon.com/",
            "description": "Create a bucket and IAM user with S3 permissions",
            "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME", "AWS_REGION"]
        },
        {
            "name": "ChromaDB Cloud (Vector DB)",
            "url": "https://cloud.trychroma.com/",
            "description": "Create an account and instance",
            "env_vars": ["CHROMA_AUTH_TOKEN", "CHROMA_API_URL"]
        },
        {
            "name": "OpenAI (AI Services)",
            "url": "https://platform.openai.com/api-keys",
            "description": "Get your API key",
            "env_vars": ["OPENAI_API_KEY"]
        },
        {
            "name": "Railway (Hosting)",
            "url": "https://railway.app/",
            "description": "Create a new project and deploy",
            "env_vars": ["All environment variables"]
        }
    ]
    
    print("This script will help you set up all required external services.")
    print("You'll need to create accounts and get API keys/connection strings.")
    
    for service in services:
        print_service(
            service["name"],
            service["url"],
            service["description"],
            service["env_vars"]
        )
    
    # Create service setup guide
    create_service_guide()
    
    print_header("Setup Complete! 🎉")
    print("You've opened all the required services.")
    print("Follow the SERVICE_SETUP_GUIDE.md for detailed instructions.")
    print("\nNext steps:")
    print("1. Set up all services and get credentials")
    print("2. Add environment variables to Railway")
    print("3. Run: python deploy_to_railway.py")

if __name__ == "__main__":
    main()
