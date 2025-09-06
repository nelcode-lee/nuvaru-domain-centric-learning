#!/bin/bash

# Start Production Services Locally (without Docker)
set -e

echo "🚀 Starting Nuvaru RAG System (Production Local)..."

# Kill any existing processes
echo "🛑 Stopping existing processes..."
pkill -f "uvicorn\|next\|http.server" 2>/dev/null || true

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start it first:"
    echo "   brew services start postgresql@15"
    exit 1
fi

# Check if ChromaDB is available (we'll use the simple vector service for now)
echo "📊 Using file-based vector database for local development"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Copy production environment if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from production template..."
    cp production.env .env
    echo "⚠️  Please edit .env file with your actual API keys:"
    echo "   - Set OPENAI_API_KEY for OpenAI services"
    echo "   - Set ANTHROPIC_API_KEY for Anthropic services"
    echo "   - Update SECRET_KEY for security"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r backend/requirements.txt

# Start backend
echo "🌐 Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start. Check the logs above."
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check the logs above."
    exit 1
fi

# Start simple HTTP server for beautiful frontend
echo "🌐 Starting beautiful frontend server..."
python3 -m http.server 8080 &
HTTP_PID=$!

echo ""
echo "🎉 Production system is running locally!"
echo ""
echo "🌐 Access your system:"
echo "   Beautiful Frontend: http://localhost:8080/beautiful_frontend.html"
echo "   React Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 System Status:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo "   HTTP Server PID: $HTTP_PID"
echo ""
echo "🛑 To stop the system:"
echo "   kill $BACKEND_PID $FRONTEND_PID $HTTP_PID"
echo ""
echo "⚠️  Configuration:"
echo "   - Edit .env file to add your API keys"
echo "   - Backend uses PostgreSQL database: nuvaru_db"
echo "   - Vector database uses file-based storage"
echo "   - LLM services require API keys in .env file"


