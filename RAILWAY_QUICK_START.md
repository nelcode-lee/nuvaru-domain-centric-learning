# 🚀 Railway Quick Start Guide

## Option 1: Automated Deployment (Recommended)

Run the deployment wizard that will guide you through everything:

```bash
python3 railway_deployment_wizard.py
```

This interactive script will:
- ✅ Check prerequisites
- ✅ Guide you through external services setup
- ✅ Set up Railway project
- ✅ Configure environment variables
- ✅ Deploy to Railway
- ✅ Test deployment
- ✅ Guide frontend deployment

## Option 2: Manual Deployment

### Step 1: Prerequisites
```bash
# Check you have the required tools
python3 --version  # Should be 3.8+
node --version     # Should be 16+
git --version      # Should be 2.0+

# Install Railway CLI
npm install -g @railway/cli
```

### Step 2: External Services Setup

#### 1. Neon DB (Database)
- Go to https://console.neon.tech/
- Create project → Copy connection string
- Save: `NEON_DATABASE_URL=postgresql://...`

#### 2. AWS S3 (File Storage)
- Go to https://s3.console.aws.amazon.com/
- Create bucket → Create IAM user → Get credentials
- Save: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`

#### 3. ChromaDB Cloud (Vector DB)
- Go to https://cloud.trychroma.com/
- Create account → Create instance → Get credentials
- Save: `CHROMA_AUTH_TOKEN`, `CHROMA_API_URL`

#### 4. OpenAI (AI)
- Go to https://platform.openai.com/api-keys
- Create API key
- Save: `OPENAI_API_KEY=sk-proj-...`

### Step 3: Railway Deployment
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables (replace with your values)
railway variables set SECRET_KEY="your-super-secret-key"
railway variables set NEON_DATABASE_URL="postgresql://..."
railway variables set OPENAI_API_KEY="sk-proj-..."
railway variables set AWS_ACCESS_KEY_ID="your-key"
railway variables set AWS_SECRET_ACCESS_KEY="your-secret"
railway variables set S3_BUCKET_NAME="your-bucket"
railway variables set CHROMA_AUTH_TOKEN="your-token"
railway variables set CHROMA_API_URL="https://your-instance.chromadb.com"

# Deploy
railway up
```

### Step 4: Frontend Deployment

#### Option A: Vercel (Recommended)
1. Go to https://vercel.com/
2. Import GitHub repository
3. Set build command: `npm run build`
4. Set output directory: `build`
5. Add environment variable:
   - `REACT_APP_API_URL=https://your-railway-app.railway.app`
6. Deploy!

#### Option B: Netlify
1. Go to https://netlify.com/
2. Connect GitHub repository
3. Set build command: `npm run build`
4. Set publish directory: `build`
5. Add environment variable:
   - `REACT_APP_API_URL=https://your-railway-app.railway.app`
6. Deploy!

## 🔧 Environment Variables Reference

### Required for Production:
```bash
# Database
NEON_DATABASE_URL=postgresql://username:password@host:port/database

# File Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# Vector Database
CHROMA_AUTH_TOKEN=your-chroma-token
CHROMA_API_URL=https://your-instance.chromadb.com

# AI Services
OPENAI_API_KEY=sk-proj-your-openai-key

# Security
SECRET_KEY=your-very-strong-secret-key
```

### Optional (with defaults):
```bash
# Application
APP_NAME="Nuvaru Domain-Centric Learning Platform"
DEBUG=false
ENVIRONMENT=production
PORT=8000

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

### 2. API Documentation
Visit: `https://your-app.railway.app/docs`

### 3. Authentication Test
```bash
# Register user
curl -X POST https://your-app.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST https://your-app.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Could not validate credentials"**
   - Check SECRET_KEY is set correctly
   - Verify token format

2. **Database connection failed**
   - Check NEON_DATABASE_URL format
   - Ensure SSL is enabled

3. **S3 upload failed**
   - Verify AWS credentials
   - Check bucket permissions

4. **ChromaDB connection failed**
   - Check CHROMA_API_URL
   - Verify auth token

### Debug Commands:
```bash
# Check Railway logs
railway logs

# Check Railway status
railway status

# Check environment variables
railway variables

# Open in browser
railway open
```

## 💰 Cost Estimation

| Service | Free Tier | Production Cost |
|---------|-----------|-----------------|
| Railway | 500 hours/month | $5-20/month |
| Neon DB | 0.5GB | $0-19/month |
| AWS S3 | 5GB | ~$0.023/GB |
| ChromaDB Cloud | 1GB | $0-25/month |
| OpenAI | Pay per use | ~$0.002/1K tokens |
| Vercel | Unlimited | $0-20/month |
| **Total** | **Free** | **~$5-65/month** |

## 🎯 Success Checklist

- [ ] Backend deployed to Railway
- [ ] Health endpoint working
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] Database connected
- [ ] File upload working
- [ ] AI chat working
- [ ] Frontend deployed
- [ ] End-to-end testing complete

## 📞 Support

- **Railway**: [Discord](https://discord.gg/railway) | [Docs](https://docs.railway.app/)
- **Neon**: [Discord](https://discord.gg/neondatabase) | [Docs](https://neon.tech/docs)
- **ChromaDB**: [Discord](https://discord.gg/chroma) | [Docs](https://docs.trychroma.com/)
- **AWS**: [Support Center](https://console.aws.amazon.com/support/)
- **OpenAI**: [Help Center](https://help.openai.com/)
- **Vercel**: [Discord](https://discord.gg/vercel) | [Docs](https://vercel.com/docs)

---

**🎉 Ready to deploy? Run the wizard: `python3 railway_deployment_wizard.py`**
