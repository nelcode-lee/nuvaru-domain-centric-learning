#!/bin/bash

echo "🚀 Starting Nuvaru RAG System (Simple Version)..."

# Kill any existing processes
pkill -f "uvicorn\|next" 2>/dev/null || true

# Start backend
echo "🌐 Starting backend..."
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend
sleep 8

echo ""
echo "🎉 System is starting up!"
echo ""
echo "🌐 Access your system:"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "⏳ Please wait a moment for both services to fully start..."
echo "   Then open http://localhost:3000 in your browser"

# Keep running
wait


