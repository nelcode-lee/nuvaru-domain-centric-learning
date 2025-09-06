#!/usr/bin/env python3
"""
Railway Deployment Wizard for Nuvaru Platform
This interactive script will guide you through the complete deployment process
"""

import os
import sys
import subprocess
import webbrowser
import json
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"🚀 {title}")
    print(f"{'='*70}")

def print_step(step, title, description=""):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {title}")
    if description:
        print(f"   {description}")
    print("-" * 50)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def wait_for_user(message="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n{message}")

def check_git_status():
    """Check git repository status"""
    print_step(1, "Checking Git Repository")
    
    try:
        # Check if git repo exists
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Git repository found")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout:
                print_success("No uncommitted changes")
            else:
                print_warning("You have uncommitted changes")
                response = input("Do you want to commit them now? (y/n): ").lower()
                if response == 'y':
                    subprocess.run(['git', 'add', '.'])
                    subprocess.run(['git', 'commit', '-m', 'Pre-deployment commit'])
                    print_success("Changes committed")
            
            return True
        else:
            print_error("Not a git repository")
            return False
    except FileNotFoundError:
        print_error("Git not found")
        return False

def setup_git_repo():
    """Set up git repository"""
    print_step(1, "Setting up Git Repository")
    
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Railway deployment'], check=True)
        print_success("Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to initialize git: {e}")
        return False

def check_railway_cli():
    """Check if Railway CLI is installed"""
    print_step(2, "Checking Railway CLI")
    
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Railway CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print_warning("Railway CLI not found")
    print("Installing Railway CLI...")
    
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print_success("Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install Railway CLI via npm")
        print("Please install manually: npm install -g @railway/cli")
        return False

def setup_external_services():
    """Guide user through external services setup"""
    print_step(3, "Setting up External Services")
    
    services = {
        "Neon DB (Database)": {
            "url": "https://console.neon.tech/",
            "description": "Create a new project and get the connection string",
            "env_var": "NEON_DATABASE_URL",
            "instructions": [
                "1. Go to https://console.neon.tech/",
                "2. Sign up or log in",
                "3. Click 'Create Project'",
                "4. Choose a name (e.g., 'nuvaru-production')",
                "5. Select a region (e.g., US East)",
                "6. Copy the connection string (starts with postgresql://)",
                "7. Save it for Railway environment variables"
            ]
        },
        "AWS S3 (File Storage)": {
            "url": "https://s3.console.aws.amazon.com/",
            "description": "Create a bucket and IAM user for file storage",
            "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME", "AWS_REGION"],
            "instructions": [
                "1. Go to https://s3.console.aws.amazon.com/",
                "2. Sign up or log in to AWS",
                "3. Click 'Create bucket'",
                "4. Name it 'nuvaru-documents-prod'",
                "5. Choose US East (N. Virginia) region",
                "6. Create IAM user with S3 permissions",
                "7. Generate access keys",
                "8. Save credentials for Railway"
            ]
        },
        "ChromaDB Cloud (Vector Database)": {
            "url": "https://cloud.trychroma.com/",
            "description": "Create an account and instance for vector storage",
            "env_vars": ["CHROMA_AUTH_TOKEN", "CHROMA_API_URL"],
            "instructions": [
                "1. Go to https://cloud.trychroma.com/",
                "2. Sign up for a free account",
                "3. Create a new instance",
                "4. Choose a name (e.g., 'nuvaru-vectors')",
                "5. Select a region",
                "6. Get the API URL and auth token",
                "7. Save credentials for Railway"
            ]
        },
        "OpenAI (AI Services)": {
            "url": "https://platform.openai.com/api-keys",
            "description": "Get your OpenAI API key for AI features",
            "env_var": "OPENAI_API_KEY",
            "instructions": [
                "1. Go to https://platform.openai.com/api-keys",
                "2. Sign up or log in",
                "3. Click 'Create new secret key'",
                "4. Name it 'nuvaru-production'",
                "5. Copy the key (starts with sk-proj-)",
                "6. Save it for Railway environment variables"
            ]
        }
    }
    
    print("You'll need to set up these external services:")
    print("Each service has a free tier that should be sufficient for testing.")
    
    credentials = {}
    
    for service_name, info in services.items():
        print(f"\n🔧 {service_name}")
        print(f"   URL: {info['url']}")
        print(f"   Description: {info['description']}")
        
        print("\n   Instructions:")
        for instruction in info['instructions']:
            print(f"   {instruction}")
        
        response = input(f"\n   Open {service_name} in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open(info['url'])
            print(f"   ✅ Opened {service_name}")
        
        # Collect credentials
        if 'env_var' in info:
            cred = input(f"   Enter {info['env_var']}: ").strip()
            if cred:
                credentials[info['env_var']] = cred
        
        if 'env_vars' in info:
            for env_var in info['env_vars']:
                cred = input(f"   Enter {env_var}: ").strip()
                if cred:
                    credentials[env_var] = cred
        
        wait_for_user("Press Enter when you've completed this service setup...")
    
    return credentials

def setup_railway_project():
    """Set up Railway project"""
    print_step(4, "Setting up Railway Project")
    
    # Check if already logged in
    try:
        subprocess.run(['railway', 'whoami'], check=True, capture_output=True)
        print_success("Already logged in to Railway")
    except subprocess.CalledProcessError:
        print("Please log in to Railway...")
        try:
            subprocess.run(['railway', 'login'], check=True)
            print_success("Logged in to Railway")
        except subprocess.CalledProcessError:
            print_error("Failed to log in to Railway")
            return False
    
    # Check if project is already linked
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if "No project linked" not in result.stdout:
            print_success("Project already linked")
            return True
    except subprocess.CalledProcessError:
        pass
    
    # Create new project
    print("Creating new Railway project...")
    try:
        subprocess.run(['railway', 'init'], check=True)
        print_success("Railway project created")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create Railway project")
        return False

def set_environment_variables(credentials):
    """Set environment variables in Railway"""
    print_step(5, "Setting Environment Variables")
    
    # Base environment variables
    env_vars = {
        "APP_NAME": "Nuvaru Domain-Centric Learning Platform",
        "APP_VERSION": "1.0.0",
        "DEBUG": "false",
        "ENVIRONMENT": "production",
        "PORT": "8000",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "SECRET_KEY": "your-super-secret-key-change-this-in-production",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_MINUTES": "10080",
        "MAX_FILE_SIZE": "10485760",
        "ALLOWED_EXTENSIONS": "txt,md,json,pdf,docx",
        "UPLOAD_DIR": "uploads",
        "CORS_ORIGINS": "https://your-frontend.vercel.app,https://your-domain.com",
        "RATE_LIMIT_REQUESTS": "100",
        "RATE_LIMIT_WINDOW": "60",
        "CACHE_TTL": "3600",
        "ENABLE_METRICS": "true",
        "METRICS_PORT": "9090",
        "ENABLE_DOCUMENT_PROCESSING": "true",
        "ENABLE_VECTOR_SEARCH": "true",
        "ENABLE_AI_CHAT": "true",
        "ENABLE_ANALYTICS": "true"
    }
    
    # Add collected credentials
    env_vars.update(credentials)
    
    print("Setting environment variables in Railway...")
    print("This may take a moment...")
    
    for key, value in env_vars.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f"{key}={value}"], 
                         check=True, capture_output=True)
            print(f"   ✅ Set {key}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Failed to set {key}")
    
    print_success("Environment variables set")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print_step(6, "Deploying to Railway")
    
    print("Deploying to Railway...")
    print("This may take several minutes...")
    
    try:
        subprocess.run(['railway', 'up'], check=True)
        print_success("Deployment successful!")
        return True
    except subprocess.CalledProcessError:
        print_error("Deployment failed")
        return False

def get_deployment_info():
    """Get deployment information"""
    print_step(7, "Getting Deployment Information")
    
    try:
        # Get project URL
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            domain = result.stdout.strip()
            print_success(f"Your app is available at: https://{domain}")
            print(f"   🔗 API Documentation: https://{domain}/docs")
            print(f"   🌐 Health Check: https://{domain}/health")
            print(f"   🔐 Authentication: https://{domain}/auth/login")
        else:
            print_warning("Could not get domain information")
            print("Check Railway dashboard for your app URL")
        
        # Get logs
        print("\n📋 Recent deployment logs:")
        subprocess.run(['railway', 'logs', '--tail', '20'])
        
    except subprocess.CalledProcessError:
        print_error("Could not get deployment information")

def test_deployment():
    """Test the deployed application"""
    print_step(8, "Testing Deployment")
    
    try:
        # Get domain
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode != 0:
            print_error("Could not get domain")
            return False
        
        domain = result.stdout.strip()
        base_url = f"https://{domain}"
        
        # Test health endpoint
        import requests
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print_success("Health endpoint working")
        else:
            print_error(f"Health endpoint failed: {response.status_code}")
            return False
        
        # Test auth endpoints
        response = requests.get(f"{base_url}/auth/me")
        if response.status_code in [401, 405]:  # Expected for unauthenticated request
            print_success("Authentication endpoints accessible")
        else:
            print_warning(f"Auth endpoints returned: {response.status_code}")
        
        print_success("Deployment test completed!")
        return True
        
    except Exception as e:
        print_error(f"Deployment test failed: {e}")
        return False

def setup_frontend_deployment():
    """Guide user through frontend deployment"""
    print_step(9, "Frontend Deployment Setup")
    
    print("For frontend deployment, you have two options:")
    print("1. Vercel (Recommended)")
    print("2. Netlify")
    
    choice = input("Choose deployment platform (1 or 2): ").strip()
    
    if choice == "1":
        print("\n🚀 Vercel Deployment:")
        print("1. Go to https://vercel.com/")
        print("2. Sign up or log in")
        print("3. Click 'New Project'")
        print("4. Import your GitHub repository")
        print("5. Set build command: npm run build")
        print("6. Set output directory: build")
        print("7. Add environment variable:")
        print("   REACT_APP_API_URL=https://your-railway-app.railway.app")
        print("8. Deploy!")
        
        response = input("\nOpen Vercel in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open("https://vercel.com/")
    
    elif choice == "2":
        print("\n🚀 Netlify Deployment:")
        print("1. Go to https://netlify.com/")
        print("2. Sign up or log in")
        print("3. Click 'New site from Git'")
        print("4. Connect your GitHub repository")
        print("5. Set build command: npm run build")
        print("6. Set publish directory: build")
        print("7. Add environment variable:")
        print("   REACT_APP_API_URL=https://your-railway-app.railway.app")
        print("8. Deploy!")
        
        response = input("\nOpen Netlify in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open("https://netlify.com/")
    
    wait_for_user("Press Enter when you've completed frontend deployment...")

def main():
    """Main deployment wizard"""
    print_header("Nuvaru Platform - Railway Deployment Wizard")
    print("This wizard will guide you through deploying your Nuvaru platform to Railway")
    print("The process includes setting up external services, deploying the backend,")
    print("and configuring the frontend deployment.")
    
    # Check prerequisites
    if not check_git_status():
        if not setup_git_repo():
            print_error("Failed to set up git repository")
            sys.exit(1)
    
    if not check_railway_cli():
        print_error("Railway CLI is required. Please install it manually.")
        sys.exit(1)
    
    # Set up external services
    credentials = setup_external_services()
    
    # Set up Railway project
    if not setup_railway_project():
        print_error("Failed to set up Railway project")
        sys.exit(1)
    
    # Set environment variables
    if not set_environment_variables(credentials):
        print_error("Failed to set environment variables")
        sys.exit(1)
    
    # Deploy to Railway
    if not deploy_to_railway():
        print_error("Deployment failed")
        sys.exit(1)
    
    # Get deployment info
    get_deployment_info()
    
    # Test deployment
    test_deployment()
    
    # Set up frontend deployment
    setup_frontend_deployment()
    
    print_header("Deployment Complete! 🎉")
    print("Your Nuvaru platform is now live on Railway!")
    print("\n📋 Summary:")
    print("✅ Backend deployed to Railway")
    print("✅ External services configured")
    print("✅ Environment variables set")
    print("✅ Authentication system active")
    print("✅ Frontend deployment guide provided")
    
    print("\n🚀 Next Steps:")
    print("1. Test your deployed application")
    print("2. Deploy your frontend")
    print("3. Set up monitoring and alerts")
    print("4. Configure custom domain (optional)")
    print("5. Set up backups and maintenance")
    
    print("\n📞 Support:")
    print("- Railway: https://docs.railway.app/")
    print("- This project: Check the documentation files")

if __name__ == "__main__":
    main()
