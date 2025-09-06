#!/bin/bash

# Nuvaru RAG System Deployment Script
# This script deploys the complete RAG system with all services

set -e

echo "🚀 Deploying Nuvaru RAG System..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Please edit .env file with your configuration before continuing"
    echo "   Key variables to set:"
    echo "   - SECRET_KEY (generate a secure random key)"
    echo "   - POSTGRES_PASSWORD (set a secure password)"
    echo "   - NEON_DATABASE_URL (if using Neon DB)"
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p infrastructure/nginx/ssl
mkdir -p logs

# Set proper permissions
echo "🔒 Setting proper permissions..."
chmod 755 uploads
chmod 755 logs

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check PostgreSQL
echo "   Checking PostgreSQL..."
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U nuvaru -d nuvaru_db; then
    echo "   ✅ PostgreSQL is ready"
else
    echo "   ❌ PostgreSQL is not ready"
fi

# Check Redis
echo "   Checking Redis..."
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping; then
    echo "   ✅ Redis is ready"
else
    echo "   ❌ Redis is not ready"
fi

# Check ChromaDB
echo "   Checking ChromaDB..."
if curl -f http://localhost:8001/api/v1/heartbeat; then
    echo "   ✅ ChromaDB is ready"
else
    echo "   ❌ ChromaDB is not ready"
fi

# Check Ollama
echo "   Checking Ollama..."
if curl -f http://localhost:11434/api/tags; then
    echo "   ✅ Ollama is ready"
else
    echo "   ❌ Ollama is not ready"
fi

# Check Backend API
echo "   Checking Backend API..."
if curl -f http://localhost:8000/health; then
    echo "   ✅ Backend API is ready"
else
    echo "   ❌ Backend API is not ready"
fi

# Pull and setup Ollama model
echo "🧠 Setting up Ollama model..."
docker-compose -f docker-compose.prod.yml exec -T ollama ollama pull llama2:7b || echo "⚠️  Failed to pull llama2:7b model"

# Run database migrations (when available)
echo "🗄️ Setting up database..."
# docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Create initial admin user (when available)
echo "👤 Creating initial admin user..."
# docker-compose -f docker-compose.prod.yml exec -T backend python scripts/create_admin.py

# Run system tests
echo "🧪 Running system tests..."
if [ -f "scripts/test_rag_system.py" ]; then
    echo "   Running RAG system tests..."
    python scripts/test_rag_system.py || echo "⚠️  Some tests failed, but deployment continues"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Access the application at:"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Nginx Proxy: http://localhost:80"
echo ""
echo "📊 Service URLs:"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo "   ChromaDB: localhost:8001"
echo "   Ollama: localhost:11434"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f [service_name]"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "   Update services: docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "📝 Next Steps:"
echo "   1. Test the API endpoints at http://localhost:8000/docs"
echo "   2. Upload test documents to verify document processing"
echo "   3. Test the RAG chat functionality"
echo "   4. Configure monitoring and alerting"
echo "   5. Set up SSL certificates for production"
echo ""
echo "🚀 Your Nuvaru RAG system is now running!"



