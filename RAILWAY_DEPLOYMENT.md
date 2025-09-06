# 🚀 Railway Deployment Guide

## Prerequisites

1. **Railway Account** ✅ (You have the Hobby subscription)
2. **Git Repository** (We'll set this up)
3. **Environment Variables** (We'll configure these)

## Step 1: Initialize Git Repository

```bash
# In your project root
git init
git add .
git commit -m "Initial commit for Railway deployment"
```

## Step 2: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or using curl
curl -fsSL https://railway.app/install.sh | sh
```

## Step 3: Login to Railway

```bash
railway login
```

## Step 4: Create Railway Project

```bash
# Initialize Railway project
railway init

# This will:
# - Create a new project in your Railway dashboard
# - Generate a railway.toml file
# - Set up the project structure
```

## Step 5: Set Environment Variables

In your Railway dashboard, go to your project and add these environment variables:

### Required Variables:
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

### Database Variables (Neon DB):
```
NEON_DATABASE_URL=your_neon_database_url_here
```

### Optional Variables:
```
ENVIRONMENT=production
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]
```

## Step 6: Deploy to Railway

```bash
# Deploy the application
railway up

# Check deployment status
railway status

# View logs
railway logs
```

## Step 7: Get Your Railway URL

```bash
# Get the deployed URL
railway domain

# Or check in Railway dashboard
```

## Step 8: Deploy Frontend (Separate Service)

The React frontend should be deployed separately. You can use:

1. **Vercel** (Recommended)
2. **Netlify**
3. **Railway** (as a separate service)

### For Vercel:
```bash
cd react-frontend
npm install -g vercel
vercel --prod
```

## Environment Variables Summary

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |
| `SECRET_KEY` | JWT secret key (generate with: `openssl rand -hex 32`) | ✅ |
| `ALGORITHM` | JWT algorithm (HS256) | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (480 = 8 hours) | ✅ |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token expiration (10080 = 7 days) | ✅ |
| `NEON_DATABASE_URL` | Neon database connection string | ✅ |
| `ENVIRONMENT` | Environment (production) | Optional |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | Optional |

## Troubleshooting

### Common Issues:

1. **Port Binding Error**
   - Railway automatically sets the `PORT` environment variable
   - Our app uses `os.getenv("PORT", 8000)` which handles this

2. **Database Connection**
   - Make sure `NEON_DATABASE_URL` is set correctly
   - Test the connection string locally first

3. **OpenAI API Key**
   - Ensure the API key is valid and has credits
   - Test with: `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models`

4. **Build Failures**
   - Check the build logs in Railway dashboard
   - Ensure all dependencies are in `requirements.txt`

### Useful Commands:

```bash
# Check Railway status
railway status

# View logs
railway logs

# Connect to Railway shell
railway shell

# Set environment variables
railway variables set KEY=value

# Deploy specific service
railway up --service backend
```

## Cost Optimization

With Railway Hobby plan:
- **$5/month** for the plan
- **$0.10/GB-hour** for compute
- **$0.10/GB** for storage

Estimated monthly cost: **$5-15** depending on usage.

## Next Steps After Deployment

1. **Test the API endpoints**
2. **Deploy the React frontend**
3. **Set up custom domain** (optional)
4. **Configure monitoring** (optional)
5. **Set up backups** (optional)

## Support

- Railway Docs: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app/

