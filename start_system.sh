#!/bin/bash

# Complete Nuvaru RAG System Startup Script
echo "🚀 Starting Nuvaru RAG System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./scripts/setup_dev.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Start backend in background
echo "🌐 Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check the logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "🌐 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend is starting up..."
fi

echo ""
echo "🎉 Nuvaru RAG System is starting up!"
echo ""
echo "🌐 Access your system:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Features available:"
echo "   • AI Chat Interface"
echo "   • Document Upload & Management"
echo "   • Knowledge Base Search"
echo "   • Real-time RAG Responses"
echo ""
echo "🛑 To stop the system:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "⏳ Please wait a moment for both services to fully start..."
echo "   Then open http://localhost:3000 in your browser"

# Keep script running
wait


