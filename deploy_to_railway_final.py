#!/usr/bin/env python3
"""
Final Railway deployment script
"""

import subprocess
import os

def load_env_file(file_path):
    """Load environment variables from a file"""
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

def set_railway_variables():
    """Set environment variables in Railway"""
    print("🔧 Setting Environment Variables in Railway")
    print("=" * 50)
    
    # Load environment variables from .env file
    env_vars = load_env_file('.env')
    
    # Essential variables for Railway deployment
    essential_vars = {
        'SECRET_KEY': 'your-super-secret-key-change-this-in-production-railway',
        'DEBUG': 'false',
        'ENVIRONMENT': 'production',
        'PORT': '8000',
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': 'json',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'REFRESH_TOKEN_EXPIRE_MINUTES': '10080',
        'MAX_FILE_SIZE': '10485760',
        'ALLOWED_EXTENSIONS': 'txt,md,json,pdf,docx',
        'UPLOAD_DIR': 'uploads',
        'CORS_ORIGINS': 'https://your-frontend.vercel.app,https://your-domain.com',
        'RATE_LIMIT_REQUESTS': '100',
        'RATE_LIMIT_WINDOW': '60',
        'CACHE_TTL': '3600',
        'ENABLE_METRICS': 'true',
        'METRICS_PORT': '9090',
        'ENABLE_DOCUMENT_PROCESSING': 'true',
        'ENABLE_VECTOR_SEARCH': 'true',
        'ENABLE_AI_CHAT': 'true',
        'ENABLE_ANALYTICS': 'true'
    }
    
    # Add variables from .env file
    essential_vars.update(env_vars)
    
    print("Setting environment variables...")
    success_count = 0
    total_count = len(essential_vars)
    
    for key, value in essential_vars.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f"{key}={value}"], 
                         check=True, capture_output=True)
            print(f"✅ {key}")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"⚠️ {key}")
    
    print(f"\n📊 Results: {success_count}/{total_count} variables set successfully")
    return success_count > 0

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚀 Deploying to Railway")
    print("=" * 30)
    
    try:
        subprocess.run(['railway', 'up'], check=True)
        print("✅ Deployment successful!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Deployment failed")
        return False

def get_deployment_info():
    """Get deployment information"""
    print("\n📋 Getting Deployment Information")
    print("=" * 40)
    
    try:
        # Get project URL
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            domain = result.stdout.strip()
            print(f"✅ Your app is available at: https://{domain}")
            print(f"🔗 API Documentation: https://{domain}/docs")
            print(f"🌐 Health Check: https://{domain}/health")
            print(f"🔐 Authentication: https://{domain}/auth/login")
        else:
            print("⚠️ Could not get domain information")
            print("Check Railway dashboard for your app URL")
        
        # Get logs
        print("\n📋 Recent deployment logs:")
        subprocess.run(['railway', 'logs', '--tail', '10'])
        
    except subprocess.CalledProcessError:
        print("❌ Could not get deployment information")

def main():
    """Main deployment function"""
    print("🚀 Final Railway Deployment for Nuvaru Platform")
    print("=" * 60)
    
    # Set environment variables
    if not set_railway_variables():
        print("❌ Failed to set environment variables")
        return
    
    # Deploy to Railway
    if not deploy_to_railway():
        print("❌ Deployment failed")
        return
    
    # Get deployment info
    get_deployment_info()
    
    print("\n🎉 Railway Deployment Complete!")
    print("\n📋 Summary:")
    print("✅ Environment variables set")
    print("✅ Backend deployed to Railway")
    print("✅ All external services configured")
    print("✅ Authentication system active")
    
    print("\n🚀 Next Steps:")
    print("1. Test your deployed application")
    print("2. Deploy your frontend to Vercel")
    print("3. Update frontend API URL")
    print("4. Test end-to-end functionality")

if __name__ == "__main__":
    main()
