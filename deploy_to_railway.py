#!/usr/bin/env python3
"""
Comprehensive Railway deployment script for Nuvaru Platform
This script will guide you through the entire deployment process
"""

import os
import sys
import subprocess
import json
import webbrowser
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_requirements():
    """Check if all requirements are met"""
    print_header("Checking Requirements")
    
    requirements = {
        "Git": ["git", "--version"],
        "Node.js": ["node", "--version"],
        "Python": ["python", "--version"]
    }
    
    missing = []
    
    for name, cmd in requirements.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: {result.stdout.strip()}")
            else:
                missing.append(name)
        except FileNotFoundError:
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        print("Please install the missing requirements and try again.")
        return False
    
    return True

def check_railway_cli():
    """Check if Railway CLI is installed"""
    print_step(1, "Checking Railway CLI")
    
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Railway CLI not found")
    print("Installing Railway CLI...")
    
    try:
        # Try npm first
        subprocess.run(["npm", "install", "-g", "@railway/cli"], check=True)
        print("✅ Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try curl as fallback
            subprocess.run([
                "curl", "-fsSL", "https://railway.app/install.sh"
            ], check=True, shell=True)
            print("✅ Railway CLI installed via curl")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Railway CLI")
            print("Please install manually: npm install -g @railway/cli")
            return False

def setup_git():
    """Set up Git repository"""
    print_step(2, "Setting up Git Repository")
    
    try:
        # Check if already a git repo
        subprocess.run(["git", "status"], check=True, capture_output=True)
        print("✅ Git repository already exists")
    except subprocess.CalledProcessError:
        print("Initializing Git repository...")
        try:
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit for Railway deployment"], check=True)
            print("✅ Git repository initialized")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize Git: {e}")
            return False
    
    return True

def setup_railway_project():
    """Set up Railway project"""
    print_step(3, "Setting up Railway Project")
    
    # Check if already logged in
    try:
        subprocess.run(["railway", "whoami"], check=True, capture_output=True)
        print("✅ Already logged in to Railway")
    except subprocess.CalledProcessError:
        print("Please log in to Railway...")
        try:
            subprocess.run(["railway", "login"], check=True)
            print("✅ Logged in to Railway")
        except subprocess.CalledProcessError:
            print("❌ Failed to log in to Railway")
            return False
    
    # Check if project is already linked
    try:
        result = subprocess.run(["railway", "status"], capture_output=True, text=True)
        if "No project linked" not in result.stdout:
            print("✅ Project already linked")
            return True
    except subprocess.CalledProcessError:
        pass
    
    # Create new project
    print("Creating new Railway project...")
    try:
        subprocess.run(["railway", "init"], check=True)
        print("✅ Railway project created")
    except subprocess.CalledProcessError:
        print("❌ Failed to create Railway project")
        return False
    
    return True

def setup_environment_variables():
    """Set up environment variables"""
    print_step(4, "Setting up Environment Variables")
    
    print("📝 Required Environment Variables:")
    print("Copy these from railway.env and set them in Railway dashboard:")
    
    env_file = Path("railway.env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
            print("\n" + content)
    else:
        print("❌ railway.env file not found")
        return False
    
    print("\n🔧 To set environment variables:")
    print("1. Go to your Railway project dashboard")
    print("2. Click on 'Variables' tab")
    print("3. Add each variable from the list above")
    print("4. Make sure to replace placeholder values with real ones")
    
    input("\nPress Enter when you've set the environment variables...")
    return True

def setup_services():
    """Guide user through setting up external services"""
    print_step(5, "Setting up External Services")
    
    services = {
        "Neon DB (Database)": {
            "url": "https://console.neon.tech/",
            "description": "Create a new project and get the connection string",
            "env_var": "NEON_DATABASE_URL"
        },
        "AWS S3 (File Storage)": {
            "url": "https://s3.console.aws.amazon.com/",
            "description": "Create a bucket and IAM user with S3 permissions",
            "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME"]
        },
        "ChromaDB Cloud (Vector DB)": {
            "url": "https://cloud.trychroma.com/",
            "description": "Create an account and instance",
            "env_vars": ["CHROMA_AUTH_TOKEN", "CHROMA_API_URL"]
        },
        "OpenAI (AI)": {
            "url": "https://platform.openai.com/api-keys",
            "description": "Get your API key",
            "env_var": "OPENAI_API_KEY"
        }
    }
    
    for service_name, info in services.items():
        print(f"\n🔧 {service_name}")
        print(f"   URL: {info['url']}")
        print(f"   Description: {info['description']}")
        if 'env_var' in info:
            print(f"   Environment Variable: {info['env_var']}")
        if 'env_vars' in info:
            print(f"   Environment Variables: {', '.join(info['env_vars'])}")
        
        response = input(f"   Open {service_name} in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open(info['url'])
    
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print_step(6, "Deploying to Railway")
    
    print("🚀 Deploying to Railway...")
    try:
        subprocess.run(["railway", "up"], check=True)
        print("✅ Deployment successful!")
    except subprocess.CalledProcessError:
        print("❌ Deployment failed")
        return False
    
    return True

def get_deployment_info():
    """Get deployment information"""
    print_step(7, "Getting Deployment Information")
    
    try:
        # Get project URL
        result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
        if result.returncode == 0:
            domain = result.stdout.strip()
            print(f"🌐 Your app is available at: https://{domain}")
            print(f"🔗 API Documentation: https://{domain}/docs")
            print(f"🌐 Health Check: https://{domain}/health")
        else:
            print("❌ Could not get domain information")
            print("Check Railway dashboard for your app URL")
        
        # Get logs
        print("\n📋 Recent logs:")
        subprocess.run(["railway", "logs", "--tail", "10"])
        
    except subprocess.CalledProcessError:
        print("❌ Could not get deployment information")

def main():
    """Main deployment function"""
    print_header("Nuvaru Platform - Railway Deployment")
    print("This script will guide you through deploying your Nuvaru platform to Railway")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check Railway CLI
    if not check_railway_cli():
        sys.exit(1)
    
    # Setup Git
    if not setup_git():
        sys.exit(1)
    
    # Setup Railway project
    if not setup_railway_project():
        sys.exit(1)
    
    # Setup external services
    setup_services()
    
    # Setup environment variables
    setup_environment_variables()
    
    # Deploy to Railway
    if not deploy_to_railway():
        sys.exit(1)
    
    # Get deployment info
    get_deployment_info()
    
    print_header("Deployment Complete! 🎉")
    print("Your Nuvaru platform is now live on Railway!")
    print("\nNext steps:")
    print("1. Test your API endpoints")
    print("2. Deploy your frontend to Vercel")
    print("3. Set up monitoring and alerts")
    print("4. Configure custom domain (optional)")

if __name__ == "__main__":
    main()
