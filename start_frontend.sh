#!/bin/bash

# Start Frontend Development Server
echo "🚀 Starting Nuvaru Frontend Development Server..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js 18+ recommended. Current version: $(node --version)"
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Backend is not running. Please start it first:"
    echo "   ./start_dev.sh"
    echo ""
    echo "   Or start it in another terminal and then run this script again."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set environment variables
export NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

echo "🌐 Starting Next.js development server..."
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo ""
echo "📋 Available features:"
echo "   • AI Chat Interface"
echo "   • Document Upload & Management"
echo "   • Knowledge Base Search"
echo "   • Real-time RAG Responses"
echo ""
echo "🎉 Frontend is starting up..."

# Start the development server
npm run dev


