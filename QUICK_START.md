# Nuvaru RAG System - Quick Start Guide

## 🚀 Deploy the RAG System

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM available
- 20GB free disk space

### 1. Deploy the System
```bash
# Run the deployment script
./scripts/deploy.sh
```

### 2. Access the System
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ChromaDB**: http://localhost:8001
- **Ollama**: http://localhost:11434

## 🧪 Test the RAG System

### 1. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### 2. Test Document Upload
```bash
# Upload a test document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@test_document.txt" \
  -F "knowledge_base_id=test_kb"
```

### 3. Test RAG Chat
```bash
# Chat with the AI
curl -X POST "http://localhost:8000/api/v1/learning/chat" \
  -H "Authorization: Bearer <your-token>" \
  -F "message=What is the main topic of the uploaded documents?" \
  -F "knowledge_base_id=test_kb"
```

### 4. Run System Tests
```bash
# Run comprehensive tests
python scripts/test_rag_system.py
```

## 📊 Monitor the System

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f chroma
docker-compose -f docker-compose.prod.yml logs -f ollama
```

### Check Service Status
```bash
# Service status
docker-compose -f docker-compose.prod.yml ps

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/heartbeat
curl http://localhost:11434/api/tags
```

## 🔧 Management Commands

### Start/Stop Services
```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Update Services
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Backup Data
```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U nuvaru nuvaru_db > backup.sql

# Backup ChromaDB
docker cp $(docker-compose -f docker-compose.prod.yml ps -q chroma):/chroma/chroma ./chroma_backup
```

## 🎯 Key Features to Test

### 1. Document Processing
- Upload various file types (PDF, TXT, MD, JSON, CSV)
- Verify document chunking and vectorization
- Check document search functionality

### 2. RAG Chat
- Ask questions about uploaded documents
- Test different knowledge bases
- Verify source attribution

### 3. Learning Features
- Submit feedback on responses
- Test session management
- Check knowledge base statistics

### 4. Security
- Verify user isolation
- Test authentication and authorization
- Check data privacy

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs
   
   # Check resources
   docker system df
   ```

2. **Ollama model not available**
   ```bash
   # Pull model manually
   docker-compose -f docker-compose.prod.yml exec ollama ollama pull llama2:7b
   ```

3. **ChromaDB connection issues**
   ```bash
   # Check ChromaDB status
   curl http://localhost:8001/api/v1/heartbeat
   
   # Restart ChromaDB
   docker-compose -f docker-compose.prod.yml restart chroma
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase Docker memory limit
   ```

### Performance Optimization

1. **Increase Docker resources**
   - Memory: 8GB+ recommended
   - CPU: 4+ cores recommended

2. **Optimize ChromaDB**
   - Adjust chunk size in settings
   - Monitor memory usage

3. **Ollama optimization**
   - Use smaller models for testing
   - Adjust temperature and max tokens

## 📈 Next Steps

1. **Production Deployment**
   - Set up SSL certificates
   - Configure domain names
   - Set up monitoring and alerting

2. **Frontend Development**
   - Build React interface
   - Implement user authentication
   - Create document management UI

3. **Enterprise Features**
   - Add user management
   - Implement role-based access
   - Set up audit logging

4. **Scaling**
   - Implement load balancing
   - Set up database clustering
   - Add horizontal scaling

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **API Reference**: http://localhost:8000/docs
- **Logs**: Use `docker-compose logs` for debugging
- **Health Checks**: All services have health endpoints

Your Nuvaru RAG system is now ready for enterprise use! 🎉



