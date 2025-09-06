#!/usr/bin/env python3
"""
Railway deployment helper script
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_repo():
    """Check if we're in a git repository"""
    try:
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        print("✅ Git repository found")
        return True
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        return False

def init_git_repo():
    """Initialize git repository if needed"""
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Railway deployment'], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize git: {e}")
        return False

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        print(f"✅ Railway CLI found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("Installing Railway CLI...")
    try:
        # Try npm first
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try curl as fallback
            subprocess.run([
                'curl', '-fsSL', 'https://railway.app/install.sh'
            ], check=True, shell=True)
            print("✅ Railway CLI installed via curl")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Railway CLI")
            return False

def setup_railway_project():
    """Set up Railway project"""
    print("\n🚀 Setting up Railway project...")
    
    # Check if already logged in
    try:
        subprocess.run(['railway', 'whoami'], check=True, capture_output=True)
        print("✅ Already logged in to Railway")
    except subprocess.CalledProcessError:
        print("Please log in to Railway:")
        subprocess.run(['railway', 'login'])
    
    # Create new project
    print("Creating new Railway project...")
    subprocess.run(['railway', 'init'])
    
    print("✅ Railway project created!")

def main():
    print("🚀 Railway Deployment Setup")
    print("=" * 40)
    
    # Check git repository
    if not check_git_repo():
        print("Initializing git repository...")
        if not init_git_repo():
            sys.exit(1)
    
    # Check Railway CLI
    if not check_railway_cli():
        print("Installing Railway CLI...")
        if not install_railway_cli():
            print("Please install Railway CLI manually:")
            print("npm install -g @railway/cli")
            print("or visit: https://docs.railway.app/develop/cli")
            sys.exit(1)
    
    # Setup Railway project
    setup_railway_project()
    
    print("\n🎉 Railway setup complete!")
    print("\nNext steps:")
    print("1. Set environment variables in Railway dashboard")
    print("2. Deploy with: railway up")
    print("3. Check logs with: railway logs")

if __name__ == "__main__":
    main()

