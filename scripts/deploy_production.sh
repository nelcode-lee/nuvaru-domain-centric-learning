#!/bin/bash

# Production Deployment Script for Nuvaru RAG System
set -e

echo "🚀 Deploying Nuvaru RAG System to Production..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from production template..."
    cp production.env .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration"
    echo "   - Set OPENAI_API_KEY for OpenAI services"
    echo "   - Set ANTHROPIC_API_KEY for Anthropic services"
    echo "   - Update SECRET_KEY for security"
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p data/vector_db
mkdir -p infrastructure/nginx/ssl

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down || true

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.production.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

# Check database
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U nuvaru > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
fi

# Check ChromaDB
if curl -f http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB is healthy"
else
    echo "❌ ChromaDB health check failed"
fi

echo ""
echo "🎉 Production deployment complete!"
echo ""
echo "🌐 Access your system:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   ChromaDB: http://localhost:8001"
echo ""
echo "📊 Monitor your services:"
echo "   docker-compose -f docker-compose.production.yml ps"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🛑 To stop the system:"
echo "   docker-compose -f docker-compose.production.yml down"
echo ""
echo "⚠️  Remember to:"
echo "   1. Set up SSL certificates in infrastructure/nginx/ssl/"
echo "   2. Configure your domain name in nginx configuration"
echo "   3. Set up proper backup for PostgreSQL and ChromaDB data"
echo "   4. Monitor system resources and performance"


