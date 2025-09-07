#!/usr/bin/env python3
"""
Vercel Frontend Deployment Script for Nuvaru Platform
"""

import subprocess
import os
import json

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not found")
        return False

def install_vercel_cli():
    """Install Vercel CLI"""
    print("📦 Installing Vercel CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        print("✅ Vercel CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Vercel CLI")
        return False

def get_railway_url():
    """Get Railway URL from user"""
    print("\n🔗 Railway Backend URL Setup")
    print("=" * 40)
    print("You need to provide your Railway backend URL.")
    print("This should look like: https://your-app-name.railway.app")
    print()
    
    railway_url = input("Enter your Railway backend URL: ").strip()
    
    if not railway_url.startswith('https://'):
        railway_url = f"https://{railway_url}"
    
    return railway_url

def setup_vercel_environment(railway_url):
    """Set up environment variables for Vercel"""
    print(f"\n🔧 Setting up environment variables for Railway URL: {railway_url}")
    
    # Create .env.local file for Vercel
    env_content = f"""# Vercel Environment Variables
REACT_APP_API_URL={railway_url}
"""
    
    with open('react-frontend/.env.local', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment variables configured")

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Deploying to Vercel")
    print("=" * 30)
    
    # Change to frontend directory
    os.chdir('react-frontend')
    
    try:
        # Build the project first
        print("📦 Building React project...")
        subprocess.run(['npm', 'run', 'build'], check=True)
        print("✅ Build successful")
        
        # Deploy to Vercel
        print("🚀 Deploying to Vercel...")
        subprocess.run(['vercel', '--prod'], check=True)
        print("✅ Deployment successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False
    finally:
        # Return to root directory
        os.chdir('..')

def main():
    """Main deployment function"""
    print("🚀 Vercel Frontend Deployment for Nuvaru Platform")
    print("=" * 60)
    
    # Check Vercel CLI
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ Cannot proceed without Vercel CLI")
            return
    
    # Get Railway URL
    railway_url = get_railway_url()
    
    # Setup environment
    setup_vercel_environment(railway_url)
    
    # Deploy to Vercel
    if deploy_to_vercel():
        print("\n🎉 Frontend Deployment Complete!")
        print("\n📋 Summary:")
        print("✅ React frontend deployed to Vercel")
        print("✅ Connected to Railway backend")
        print("✅ Environment variables configured")
        
        print("\n🌐 Your Nuvaru Platform is now live!")
        print("Check your Vercel dashboard for the frontend URL")
        print("Your backend is running on Railway")
        print("Your frontend will connect to your Railway backend automatically")
        
        print("\n🚀 Next Steps:")
        print("1. Test your complete platform")
        print("2. Update CORS settings if needed")
        print("3. Test authentication flow")
        print("4. Test document upload and chat features")
    else:
        print("❌ Deployment failed. Check the errors above.")

if __name__ == "__main__":
    main()
