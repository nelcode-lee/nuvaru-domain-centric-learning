#!/usr/bin/env python3
"""
Setup GitHub repository for Railway deployment
"""

import subprocess
import webbrowser
import sys

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🐙 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_git_status():
    """Check git repository status"""
    print_step(1, "Checking Git Repository")
    
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository found")
            return True
        else:
            print("❌ Not a git repository")
            return False
    except FileNotFoundError:
        print("❌ Git not found")
        return False

def create_github_repo():
    """Guide user to create GitHub repository"""
    print_step(2, "Creating GitHub Repository")
    
    print("📝 You need to create a GitHub repository:")
    print("1. Go to https://github.com/new")
    print("2. Repository name: nuvaru-domain-centric-learning")
    print("3. Make it PUBLIC (Railway works better with public repos)")
    print("4. Don't initialize with README")
    print("5. Click 'Create repository'")
    
    response = input("\nOpen GitHub in browser? (y/n): ").lower()
    if response == 'y':
        webbrowser.open("https://github.com/new")
        print("✅ Opened GitHub")
    
    input("\nPress Enter when you've created the repository...")

def setup_remote(username):
    """Set up GitHub remote"""
    print_step(3, "Setting up GitHub Remote")
    
    remote_url = f"https://github.com/{username}/nuvaru-domain-centric-learning.git"
    
    try:
        # Remove existing remote if any
        subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
        
        # Add new remote
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        print(f"✅ Added remote: {remote_url}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to add remote: {remote_url}")
        return False

def push_to_github():
    """Push code to GitHub"""
    print_step(4, "Pushing to GitHub")
    
    try:
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
        print("✅ Successfully pushed to GitHub")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to push to GitHub")
        return False

def main():
    """Main function"""
    print_header("GitHub Repository Setup for Railway")
    print("This script will help you push your code to GitHub")
    print("so Railway can deploy it.")
    
    # Check git repository
    if not check_git_status():
        print("❌ Git repository not found. Please initialize git first.")
        sys.exit(1)
    
    # Create GitHub repository
    create_github_repo()
    
    # Get GitHub username
    username = input("\nEnter your GitHub username: ").strip()
    if not username:
        print("❌ GitHub username is required!")
        sys.exit(1)
    
    # Set up remote
    if not setup_remote(username):
        sys.exit(1)
    
    # Push to GitHub
    if not push_to_github():
        sys.exit(1)
    
    print_header("GitHub Setup Complete! 🎉")
    print("Your code is now on GitHub and ready for Railway deployment!")
    print("\n🚀 Next steps:")
    print("1. Go back to Railway")
    print("2. Connect your GitHub repository")
    print("3. Deploy!")

if __name__ == "__main__":
    main()
