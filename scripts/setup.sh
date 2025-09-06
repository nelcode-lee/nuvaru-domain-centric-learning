#!/bin/bash

# Nuvaru Platform Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Nuvaru Domain-Centric Learning Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Please edit .env file with your configuration"
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Create SSL directory for nginx
echo "🔒 Creating SSL directory..."
mkdir -p infrastructure/nginx/ssl

# Build and start services
echo "🔨 Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations (when available)
echo "🗄️ Setting up database..."
# docker-compose exec backend alembic upgrade head

# Create initial admin user (when available)
echo "👤 Creating initial admin user..."
# docker-compose exec backend python scripts/create_admin.py

echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Service URLs:"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo "   ChromaDB: localhost:8001"
echo "   Ollama: localhost:11434"
echo ""
echo "🔧 To stop the services: docker-compose down"
echo "📝 To view logs: docker-compose logs -f [service_name]"



