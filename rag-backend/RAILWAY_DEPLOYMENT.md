# Railway Deployment Guide

## Files Created for Railway Deployment

The following configuration files have been created to fix your Railway deployment:

1. **Procfile** - Tells Railway how to start your application
2. **runtime.txt** - Specifies Python version (3.11.7)
3. **railway.json** - Railway-specific configuration
4. **nixpacks.toml** - Build configuration for Nixpacks
5. **.railwayignore** - Excludes unnecessary files from deployment
6. **requirements.txt** - Fixed dependencies (removed problematic packages, added missing `cohere`)

## Changes Made

### 1. Fixed requirements.txt
- ✅ Added missing `cohere` package
- ✅ Removed `psycopg2-binary` (replaced with lighter `asyncpg`)
- ✅ Removed `pg8000` (not needed with asyncpg)
- ✅ Removed `langchain-community` and `chromadb` (not imported in main.py)
- ✅ Updated to Python 3.11-compatible versions (Railway was using Python 3.13 which broke builds)
- ✅ Created `requirements-min.txt` as fallback without heavy dependencies

### 2. Created Railway Configuration
- ✅ Procfile for start command
- ✅ runtime.txt for Python 3.11
- ✅ railway.json with health checks
- ✅ nixpacks.toml for build process

## Deployment Steps

### Step 1: Set Up Railway Project

1. Go to [Railway](https://railway.app/)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `fatimamudassir93/Hackhathon-AI-Book`

### Step 2: Configure Build Settings

1. After selecting the repo, Railway will detect your Python app
2. Set the **Root Directory** to: `rag-backend`
3. Railway will automatically use the configuration files we created

### Step 3: Add Environment Variables

In Railway, go to your project → Variables tab and add:

```env
# Required Environment Variables

# LLM Provider (at least one)
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# LLM Priority
LLM_PRIORITY=groq,gemini,openai

# Qdrant (Vector Database)
QDRANT_HOST=https://b8f23807-99c6-4ed5-bf2e-fdec7ad705f5.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Neon PostgreSQL Database
DATABASE_URL=your_neon_database_url_here

# Authentication Secret (generate with: openssl rand -base64 32)
AUTH_SECRET=your-secret-key-minimum-32-characters-long

# Optional: Cohere API (if using)
COHERE_API_KEY=your_cohere_api_key_here
```

### Step 4: Set Up PostgreSQL Database on Railway

Option 1: **Use Existing Neon Database** (Recommended if already set up)
- Just use your existing `DATABASE_URL` from Neon

Option 2: **Add Railway PostgreSQL**
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable
4. Your app will connect automatically

### Step 5: Deploy

1. Click "Deploy" in Railway
2. Monitor the build logs for any errors
3. Once deployed, Railway will provide a public URL (e.g., `https://your-app.railway.app`)

### Step 6: Update Frontend Configuration

Update your frontend to use the Railway backend URL:

In `physical-ai-book/src/theme/Root.tsx`:
```tsx
<Chatbot apiUrl="https://your-app.railway.app" />
```

## Troubleshooting Common Build Errors

### ⚠️ **CRITICAL: Python 3.13 Build Failures** (FIXED)
**Error**: `asyncpg`, `pydantic-core`, or `grpcio-tools` fail to build
**Root Cause**: Railway was auto-detecting Python 3.13, which these packages don't support yet
**Solution**: ✅ Fixed with `.python-version`, `runtime.txt`, and `nixpacks.toml` forcing Python 3.11

If you still see Python 3.13 errors:
1. Check Railway build logs for Python version
2. In Railway dashboard → Settings → Environment, add:
   ```
   PYTHON_VERSION=3.11.7
   ```
3. Redeploy

### Error: "Could not find a version that satisfies..."
**Solution**: Dependencies are already fixed in requirements.txt

### Error: "pg_config executable not found"
**Solution**: Removed psycopg2-binary, using asyncpg instead

### Error: "Module 'cohere' not found"
**Solution**: Added cohere to requirements.txt

### Error: Build timeout or heavy dependencies
**Solution**: Use the minimal requirements file:
```bash
# In Railway, change build command to:
pip install -r requirements-min.txt
```
This excludes `sentence-transformers` (1.5GB+ of dependencies)

### Error: "Address already in use"
**Solution**: Railway automatically sets $PORT - our Procfile uses it correctly

### Error: asyncpg compilation errors
**Symptoms**: Long C compilation errors about missing functions
**Solution**: Ensure Python 3.11 is being used (not 3.13). Check `.python-version` file exists.

## Health Check

Your app has a health endpoint at `/health` that Railway will use to monitor your deployment.

Test it after deployment:
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T...",
  "services": {
    "database": "connected",
    "qdrant": "connected"
  }
}
```

## Post-Deployment Checklist

- [ ] Verify build completed successfully
- [ ] Check deployment logs for startup errors
- [ ] Test `/health` endpoint
- [ ] Test `/api/chat` endpoint with authentication
- [ ] Verify database connection works
- [ ] Verify Qdrant vector search works
- [ ] Update frontend with Railway URL
- [ ] Test end-to-end chat functionality

## Monitoring

Railway provides:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History and rollback capability

Access these in your Railway project dashboard.

## Scaling

Railway automatically scales based on:
- **Memory**: Up to 8GB (check your plan)
- **CPU**: Shared cores (upgradeable)

For high traffic, consider:
1. Upgrading to Pro plan
2. Implementing Redis caching
3. Adding rate limiting (already implemented in your app)

## Cost Optimization

Railway free tier includes:
- 500 hours/month
- $5 credit

Tips to reduce costs:
1. Use Groq for LLM (free tier)
2. Keep Qdrant on their free cloud
3. Use Neon free tier for PostgreSQL
4. Set up auto-sleep for low-traffic periods

## Support

If you encounter issues:
1. Check Railway build logs
2. Review this guide
3. Check Railway documentation: https://docs.railway.app
4. Railway Discord: https://discord.gg/railway
