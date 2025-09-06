#!/bin/bash

# Nuvaru RAG System - Development Setup (No Docker)
# This script sets up the development environment without Docker

set -e

echo "🚀 Setting up Nuvaru RAG System for Development..."

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Python version: $PYTHON_VERSION"

# Check if Python 3.11+
if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 0 ]]; then
    echo "⚠️  Python 3.11+ recommended. Current version: $PYTHON_VERSION"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p data/chroma
mkdir -p data/ollama

# Set up environment file
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Environment file created from template"
    echo "📝 Please edit .env file with your configuration"
else
    echo "✅ Environment file already exists"
fi

# Create test data
echo "📄 Creating test data..."
mkdir -p test_data
cat > test_data/sample_document.txt << EOF
# Sample Medical Document

## Diabetes Management Guidelines

### Overview
Diabetes is a chronic condition that affects how your body turns food into energy. There are two main types: Type 1 and Type 2.

### Type 1 Diabetes
Type 1 diabetes is an autoimmune condition where the body attacks insulin-producing cells in the pancreas. It typically develops in children and young adults.

### Type 2 Diabetes
Type 2 diabetes is more common and occurs when the body becomes resistant to insulin or doesn't produce enough. It typically develops in adults over 45.

### Symptoms
Common symptoms include:
- Increased thirst
- Frequent urination
- Extreme fatigue
- Blurred vision
- Slow-healing sores

### Treatment
Treatment typically includes:
- Medication (insulin, metformin)
- Diet changes
- Regular exercise
- Blood sugar monitoring

### Complications
Long-term complications can include:
- Heart disease
- Kidney damage
- Nerve damage
- Eye problems
- Foot problems

### Prevention
For Type 2 diabetes:
- Maintain healthy weight
- Eat balanced diet
- Exercise regularly
- Monitor blood sugar
EOF

echo "✅ Test document created"

# Create startup script
echo "🚀 Creating startup script..."
cat > start_dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Nuvaru RAG System in Development Mode..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Start the FastAPI server
echo "🌐 Starting FastAPI server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x start_dev.sh

# Create test script
echo "🧪 Creating test script..."
cat > test_dev.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for development environment
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all modules can be imported"""
    try:
        from app.core.config import settings
        from app.services.vector_service import VectorService
        from app.services.embedding_service import EmbeddingService
        from app.services.learning_service import LearningService
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from app.core.config import settings
        print(f"✅ Configuration loaded: {settings.PROJECT_NAME}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Debug: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    print("🧪 Testing Development Environment...")
    
    if test_imports() and test_config():
        print("🎉 Development environment is ready!")
        print("\n📋 Next steps:")
        print("   1. Start the server: ./start_dev.sh")
        print("   2. Open API docs: http://localhost:8000/docs")
        print("   3. Run tests: python scripts/test_rag_system.py")
    else:
        print("❌ Development environment setup failed")

if __name__ == "__main__":
    main()
EOF

chmod +x test_dev.py

echo ""
echo "🎉 Development environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Test the setup: python test_dev.py"
echo "   3. Start the server: ./start_dev.sh"
echo "   4. Open API docs: http://localhost:8000/docs"
echo ""
echo "🔧 For production deployment with Docker:"
echo "   1. Install Docker and Docker Compose"
echo "   2. Run: ./scripts/deploy.sh"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICK_START.md"
echo "   - Development: docs/DEVELOPMENT.md"
echo "   - API Reference: http://localhost:8000/docs (after starting server)"
echo ""
echo "🚀 Your Nuvaru RAG system is ready for development!"



