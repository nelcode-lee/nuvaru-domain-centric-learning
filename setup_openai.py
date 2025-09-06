#!/usr/bin/env python3
"""
Setup script for OpenAI API key configuration
"""

import os
import sys
from pathlib import Path

def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    print("🤖 OpenAI API Key Setup")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key and current_key != "your-openai-api-key-here":
        print(f"✅ OpenAI API key is already set: {current_key[:10]}...")
        return True
    
    print("To get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/")
    print("2. Sign up or log in")
    print("3. Navigate to API Keys section")
    print("4. Create a new API key")
    print("5. Copy the key (starts with 'sk-')")
    print()
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: API key should start with 'sk-'")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Set environment variable for current session
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Create .env file
    env_file = Path(".env")
    env_content = f"""# OpenAI Configuration
OPENAI_API_KEY={api_key}

# Database Configuration (if needed)
DATABASE_URL=postgresql://user:password@localhost/nuvaru_db

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Application Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
MAX_CONTEXT_LENGTH=4000  # Maximum context length for AI responses
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"✅ API key saved to {env_file}")
    except Exception as e:
        print(f"⚠️  Could not save to .env file: {e}")
        print("You can manually set the environment variable:")
        print(f"export OPENAI_API_KEY='{api_key}'")
    
    print()
    print("✅ Setup complete! You can now restart the backend.")
    return True

def test_connection():
    """Test OpenAI connection"""
    print("\n🧪 Testing OpenAI connection...")
    
    try:
        from backend.app.services.openai_service import OpenAIService
        service = OpenAIService()
        
        if service.test_connection():
            print("✅ OpenAI connection successful!")
            return True
        else:
            print("❌ OpenAI connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

if __name__ == "__main__":
    if setup_openai_key():
        test_connection()
    else:
        print("Setup cancelled")
        sys.exit(1)

