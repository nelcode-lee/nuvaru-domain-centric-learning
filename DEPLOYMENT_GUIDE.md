# 🚀 Nuvaru Platform Deployment Guide

This guide covers deploying the Nuvaru Domain-Centric Learning Platform to production using Railway, Neon DB, AWS S3, and ChromaDB.

## 📋 Prerequisites

- GitHub account
- Railway account
- Neon DB account
- AWS account
- OpenAI API key

## 🛠 Step-by-Step Deployment

### 1. **Neon DB Setup** (Database)

1. Go to [Neon Console](https://console.neon.tech/)
2. Create a new project
3. Copy the connection string
4. Add to environment variables:
   ```bash
   NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### 2. **AWS S3 Setup** (File Storage)

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Create a new bucket (e.g., `nuvaru-documents-prod`)
3. Create IAM user with S3 permissions
4. Add to environment variables:
   ```bash
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=nuvaru-documents-prod
   ```

### 3. **ChromaDB Setup** (Vector Database)

#### Option A: Local ChromaDB (Simple)
```bash
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION_NAME=nuvaru_knowledge
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

#### Option B: ChromaDB Cloud (Production)
1. Go to [ChromaDB Cloud](https://cloud.trychroma.com/)
2. Create account and instance
3. Get API URL and auth token
4. Add to environment variables:
   ```bash
   CHROMA_AUTH_TOKEN=your-chroma-auth-token
   CHROMA_API_URL=https://your-instance.chromadb.com
   ```

### 4. **Railway Deployment** (Hosting)

1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Create new project
4. Add environment variables from `env.example`
5. Deploy!

### 5. **Frontend Deployment** (Vercel)

1. Go to [Vercel](https://vercel.com/)
2. Import your repository
3. Set build command: `npm run build`
4. Set output directory: `build`
5. Add environment variables:
   ```bash
   REACT_APP_API_URL=https://your-railway-app.railway.app
   ```

## 🔧 Environment Variables Reference

### Required for Production:
```bash
# Database
NEON_DATABASE_URL=postgresql://...

# File Storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=your-bucket

# AI
OPENAI_API_KEY=sk-proj-...

# Vector DB
CHROMA_AUTH_TOKEN=your-token
CHROMA_API_URL=https://your-instance.chromadb.com

# Railway
PORT=8000
```

### Optional (with defaults):
```bash
# Security
SECRET_KEY=your-secret-key
ENVIRONMENT=production
DEBUG=false

# CORS
BACKEND_CORS_ORIGINS=https://your-frontend.vercel.app

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

## 📊 Cost Estimation

| Service | Free Tier | Production Cost |
|---------|-----------|-----------------|
| Railway | $0 | $5-20/month |
| Neon DB | $0 | $0-19/month |
| AWS S3 | 5GB free | ~$0.023/GB |
| ChromaDB | Local free | $0-25/month |
| Vercel | $0 | $0-20/month |
| **Total** | **$0** | **~$5-65/month** |

## 🔒 Security Checklist

- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS (Railway handles this)
- [ ] Set proper CORS origins
- [ ] Use environment variables for all secrets
- [ ] Enable database SSL
- [ ] Set up monitoring (Sentry)
- [ ] Configure rate limiting

## 🚨 Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check NEON_DATABASE_URL format
   - Ensure SSL is enabled

2. **S3 Upload Failed**
   - Verify AWS credentials
   - Check bucket permissions
   - Ensure region matches

3. **ChromaDB Connection Failed**
   - Check CHROMA_API_URL
   - Verify auth token

4. **CORS Errors**
   - Update BACKEND_CORS_ORIGINS
   - Check frontend API_URL

## 📈 Scaling Considerations

- **Database**: Neon DB auto-scales
- **File Storage**: S3 scales automatically
- **Vector DB**: Consider ChromaDB Cloud for high volume
- **Hosting**: Railway scales based on usage
- **CDN**: Vercel provides global CDN

## 🔄 CI/CD Pipeline

Railway automatically deploys on git push to main branch. For more control:

1. Set up GitHub Actions
2. Add tests and linting
3. Deploy to staging first
4. Promote to production

## 📞 Support

- Railway: [Discord](https://discord.gg/railway)
- Neon: [Discord](https://discord.gg/neondatabase)
- ChromaDB: [Discord](https://discord.gg/chroma)
- AWS: [Support Center](https://console.aws.amazon.com/support/)

