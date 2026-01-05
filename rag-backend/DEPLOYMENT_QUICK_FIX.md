# Quick Fix for Railway Build Errors

## The Problem
Your build failed because Railway auto-detected **Python 3.13**, but several packages don't support it yet:
- `asyncpg` - PostgreSQL driver
- `pydantic-core` - Pydantic validation
- `grpcio-tools` - gRPC tools

## The Solution ✅

All files have been updated to force **Python 3.11**. Follow these steps:

### 1. Commit and Push Changes
```bash
cd rag-backend
git add .
git commit -m "fix: force Python 3.11 for Railway compatibility

- Add .python-version file
- Update requirements.txt with Python 3.11-compatible versions
- Add requirements-min.txt as fallback
- Update nixpacks.toml to specify Python 3.11"

git push origin 003-book-content-ingestion
```

### 2. Deploy on Railway
1. Go to your Railway project
2. It should auto-deploy after the push
3. Monitor the build logs - you should see:
   ```
   Using Python version: 3.11
   ```

### 3. If Still Failing
Add environment variable in Railway:
1. Go to your Railway project → Settings → Environment Variables
2. Add:
   - Key: `PYTHON_VERSION`
   - Value: `3.11.7`
3. Click "Redeploy"

### 4. Alternative: Use Minimal Requirements
If `sentence-transformers` is causing issues (it's 1.5GB+ of PyTorch dependencies):

In Railway → Settings → Build:
- Change build command to: `pip install -r requirements-min.txt`

This removes sentence-transformers but keeps all LLM providers and core functionality.

## Files Created/Modified

✅ **requirements.txt** - Updated to Python 3.11-compatible versions
✅ **runtime.txt** - Specifies `python-3.11.7`
✅ **.python-version** - Forces Python 3.11
✅ **nixpacks.toml** - Build config with Python 3.11
✅ **requirements-min.txt** - Lightweight fallback (no sentence-transformers)
✅ **Procfile** - Start command
✅ **railway.json** - Railway config
✅ **.railwayignore** - Exclude unnecessary files

## What Changed in requirements.txt

| Package | Old Version | New Version | Why |
|---------|------------|-------------|-----|
| pydantic | 2.5.3 ❌ | 2.6.4 ✅ | Better Python 3.11 support |
| pydantic-settings | 2.1.0 ❌ | 2.2.1 ✅ | Matches pydantic |
| sqlalchemy | 2.0.25 | 2.0.28 | Bug fixes |
| openai | 1.10.0 | 1.12.0 | Latest features |
| groq | 0.4.1 | 0.4.2 | Bug fixes |
| google-generativeai | 0.3.2 | 0.4.1 | Latest API |
| cohere | **MISSING** ❌ | 4.56 ✅ | **Added (was imported but not in requirements!)** |
| sentence-transformers | 2.3.1 | 2.5.1 | Latest version |
| qdrant-client | 1.7.3 | 1.8.2 | Latest features |
| httpx | 0.26.0 | 0.27.0 | Bug fixes |
| python-multipart | 0.0.6 | 0.0.9 | Security fixes |

Removed:
- ❌ `psycopg2-binary` - Replaced with asyncpg (lighter, faster)
- ❌ `pg8000` - Not needed with asyncpg
- ❌ `langchain-community` - Not imported in code
- ❌ `chromadb` - Not imported in code

## Expected Build Time
- **With sentence-transformers**: 5-8 minutes (downloads PyTorch ~900MB)
- **Without (requirements-min.txt)**: 2-3 minutes

## Verification
After successful deployment:

1. Check health endpoint:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. Expected response:
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

## Need Help?
If build still fails, share:
1. Railway build logs (first 50 lines)
2. Python version shown in logs
3. Specific error message

The fix should work now! 🚀
