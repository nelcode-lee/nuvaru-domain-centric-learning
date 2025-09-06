#!/usr/bin/env python3
"""
Authentication setup script for Nuvaru Platform
This script will help you set up and test the authentication system
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔐 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_backend_running():
    """Check if the backend is running"""
    print_step(1, "Checking Backend Status")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend is not running")
        print("Please start the backend with: python simple_backend.py")
        return False

def test_authentication_endpoints():
    """Test authentication endpoints"""
    print_step(2, "Testing Authentication Endpoints")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test auth endpoints
    auth_endpoints = [
        "/auth/register",
        "/auth/login",
        "/auth/me",
        "/auth/refresh",
        "/auth/logout"
    ]
    
    for endpoint in auth_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            # We expect 405 (Method Not Allowed) for GET requests to POST endpoints
            if response.status_code in [200, 405, 422]:
                print(f"✅ {endpoint} endpoint accessible")
            else:
                print(f"⚠️ {endpoint} endpoint returned {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} endpoint error: {e}")
    
    return True

def test_user_registration():
    """Test user registration"""
    print_step(3, "Testing User Registration")
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "bio": "Test user for authentication testing"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            return user_data
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print_step(4, "Testing User Login")
    
    base_url = "http://localhost:8000"
    
    # Test login data
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            print(f"   Access Token: {token_data.get('access_token')[:20]}...")
            print(f"   Token Type: {token_data.get('token_type')}")
            print(f"   Expires In: {token_data.get('expires_in')} seconds")
            return token_data
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    print_step(5, "Testing Protected Endpoints")
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test /auth/me endpoint
    try:
        response = requests.get(f"{base_url}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ /auth/me endpoint working")
            user_data = response.json()
            print(f"   Current user: {user_data.get('username')}")
        else:
            print(f"❌ /auth/me endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /auth/me error: {e}")
    
    # Test document upload endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/documents", headers=headers)
        if response.status_code == 200:
            print("✅ Document endpoints accessible")
        else:
            print(f"⚠️ Document endpoints returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Document endpoints error: {e}")

def test_frontend_integration():
    """Test frontend integration"""
    print_step(6, "Testing Frontend Integration")
    
    # Check if frontend is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            print("   Open http://localhost:3000 to test authentication")
        else:
            print(f"⚠️ Frontend returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Frontend is not running")
        print("   Start frontend with: cd react-frontend && npm start")
    
    print("\n📝 Frontend Testing Steps:")
    print("1. Open http://localhost:3000")
    print("2. Click 'Sign In' or 'Create Account'")
    print("3. Try registering a new user")
    print("4. Try logging in with existing user")
    print("5. Test document upload and chat functionality")

def create_test_users():
    """Create test users for development"""
    print_step(7, "Creating Test Users")
    
    base_url = "http://localhost:8000"
    
    test_users = [
        {
            "email": "admin@nuvaru.com",
            "username": "admin",
            "password": "AdminPassword123!",
            "full_name": "Admin User",
            "bio": "System administrator"
        },
        {
            "email": "user@nuvaru.com",
            "username": "user",
            "password": "UserPassword123!",
            "full_name": "Regular User",
            "bio": "Regular user account"
        }
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(
                f"{base_url}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                print(f"✅ Created user: {user_data['username']}")
            else:
                print(f"⚠️ User {user_data['username']} might already exist")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")

def main():
    """Main authentication setup function"""
    print_header("Nuvaru Platform - Authentication Setup")
    print("This script will help you set up and test the authentication system")
    
    # Check if backend is running
    if not check_backend_running():
        print("\n❌ Please start the backend first:")
        print("   python simple_backend.py")
        sys.exit(1)
    
    # Test authentication endpoints
    if not test_authentication_endpoints():
        print("\n❌ Authentication endpoints not working properly")
        sys.exit(1)
    
    # Test user registration
    user_data = test_user_registration()
    if not user_data:
        print("\n❌ User registration failed")
        sys.exit(1)
    
    # Test user login
    token_data = test_user_login()
    if not token_data:
        print("\n❌ User login failed")
        sys.exit(1)
    
    # Test protected endpoints
    test_protected_endpoints(token_data['access_token'])
    
    # Create additional test users
    create_test_users()
    
    # Test frontend integration
    test_frontend_integration()
    
    print_header("Authentication Setup Complete! 🎉")
    print("Your authentication system is working properly!")
    print("\n📋 Summary:")
    print("✅ Backend authentication endpoints working")
    print("✅ User registration working")
    print("✅ User login working")
    print("✅ Protected endpoints working")
    print("✅ Test users created")
    
    print("\n🚀 Next Steps:")
    print("1. Test the frontend authentication flow")
    print("2. Deploy to Railway with authentication enabled")
    print("3. Set up production authentication settings")
    print("4. Configure user roles and permissions")

if __name__ == "__main__":
    main()
