# 📋 Railway Deployment Checklist

## Before You Start
- [ ] You have a GitHub account
- [ ] You have a Railway account (free: https://railway.app)
- [ ] You have your API keys ready:
  - [ ] Groq API key (free: https://console.groq.com)
  - [ ] Qdrant API key (you already have this)
  - [ ] Neon PostgreSQL URL (you already have this)
  - [ ] Optional: Gemini, OpenAI keys

---

## Step 1: Commit & Push Changes ✅

```bash
cd C:\Users\shoai\Desktop\Hackhathon-ai-book
cd rag-backend

# Review what changed
git status

# Add all changes
git add .

# Commit
git commit -m "fix: Railway deployment with Python 3.11

- Force Python 3.11 to avoid 3.13 compatibility issues
- Add missing cohere package
- Remove heavy/unused dependencies
- Add Railway config files (Procfile, runtime.txt, nixpacks.toml)
- Create requirements-min.txt as fallback"

# Push to GitHub
git push origin 003-book-content-ingestion
```

**Checklist:**
- [ ] Changes committed
- [ ] Changes pushed to GitHub
- [ ] No errors in git push

---

## Step 2: Create Railway Project 🚂

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose: **`fatimamudassir93/Hackhathon-AI-Book`**
5. **IMPORTANT**: Click "Add variables" → Skip for now
6. Railway starts building...

**Checklist:**
- [ ] Railway project created
- [ ] GitHub repo connected

---

## Step 3: Configure Root Directory 📁

Railway needs to know your code is in `rag-backend/`:

1. In Railway project → **Settings**
2. Scroll to **"Root Directory"**
3. Set to: `rag-backend`
4. Click **"Deploy"** (if not auto-deploying)

**Checklist:**
- [ ] Root directory set to `rag-backend`
- [ ] Build restarted

---

## Step 4: Add Environment Variables 🔐

In Railway → **Variables** tab, add:

### Required Variables:
```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_HOST=https://b8f23807-99c6-4ed5-bf2e-fdec7ad705f5.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.h5HtPPCuzeICgJIXH8ccVAdCnLDaPkX5V8GJlSz8TX0
DATABASE_URL=your_neon_postgres_connection_string
AUTH_SECRET=generate-a-32-character-secret-key-here
LLM_PRIORITY=groq,gemini,openai
```

### Optional (if Python 3.13 issue persists):
```env
PYTHON_VERSION=3.11.7
```

**How to add:**
1. Click "+ New Variable"
2. Enter Name and Value
3. Click "Add"
4. Repeat for each variable

**Generate AUTH_SECRET:**
```bash
# On Windows PowerShell:
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# On Git Bash:
openssl rand -base64 32
```

**Checklist:**
- [ ] GROQ_API_KEY added
- [ ] QDRANT_HOST added
- [ ] QDRANT_API_KEY added
- [ ] DATABASE_URL added (from Neon)
- [ ] AUTH_SECRET added
- [ ] LLM_PRIORITY added

---

## Step 5: Monitor Build 📊

Watch the build logs:
1. Click on **"Deployments"** tab
2. Click on the latest deployment
3. Watch logs for:
   - ✅ `Using Python version: 3.11` (GOOD)
   - ❌ `Using Python version: 3.13` (BAD - add PYTHON_VERSION var)
   - ✅ `Successfully installed fastapi-0.109.0...` (GOOD)
   - ✅ `Build complete` (GOOD)

**Expected build time:**
- With sentence-transformers: 5-8 minutes
- Without (if using requirements-min.txt): 2-3 minutes

**Checklist:**
- [ ] Build started
- [ ] Python 3.11 detected (not 3.13)
- [ ] All packages installed successfully
- [ ] No compilation errors
- [ ] Build succeeded

---

## Step 6: Get Your Railway URL 🌐

After successful deployment:
1. Railway shows your app URL (e.g., `https://your-app.railway.app`)
2. Copy this URL

**Checklist:**
- [ ] Deployment successful
- [ ] Railway URL obtained

---

## Step 7: Test Health Endpoint 🏥

Test your deployment:
```bash
# Replace with your actual Railway URL
curl https://your-app.railway.app/health

# Or open in browser:
# https://your-app.railway.app/health
```

**Expected response:**
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

**Checklist:**
- [ ] Health endpoint returns 200 OK
- [ ] Database shows "connected"
- [ ] Qdrant shows "connected"

---

## Step 8: Update Frontend (Optional) 🎨

Update your Docusaurus frontend to use Railway backend:

**File:** `physical-ai-book/src/theme/Root.tsx`

```tsx
// Change from:
<Chatbot apiUrl="http://localhost:8000" />

// To:
<Chatbot apiUrl="https://your-app.railway.app" />
```

**Checklist:**
- [ ] Frontend updated with Railway URL
- [ ] Frontend rebuilt and tested

---

## 🎯 Troubleshooting

### Build Fails with Python 3.13
**Fix:** Add environment variable:
- Name: `PYTHON_VERSION`
- Value: `3.11.7`

### Build Times Out
**Fix:** Use minimal requirements:
1. Railway → Settings → Build
2. Custom build command: `pip install -r requirements-min.txt`

### Database Connection Fails
**Fix:** Check DATABASE_URL format:
```
postgresql://user:password@host/database?sslmode=require
```

### Qdrant Connection Fails
**Fix:** Verify QDRANT_HOST starts with `https://` and API key is correct

---

## ✅ Success Criteria

Your deployment is successful when:
- [x] Build completes without errors
- [x] Health endpoint returns healthy status
- [x] Database connects successfully
- [x] Qdrant connects successfully
- [x] Chat API responds to queries

---

## 📚 Need Help?

Check these files:
- `README_DEPLOY.md` - Quick start guide
- `DEPLOYMENT_QUICK_FIX.md` - Detailed fix explanation
- `RAILWAY_DEPLOYMENT.md` - Complete deployment guide

**Common Issues:**
1. Python 3.13 → Force 3.11 with PYTHON_VERSION env var
2. Build timeout → Use requirements-min.txt
3. Module not found → Check environment variables

---

## 🎉 You're Done!

After completing this checklist:
- ✅ Backend deployed on Railway
- ✅ Health checks passing
- ✅ Database connected
- ✅ Ready for frontend integration

**Next steps:**
1. Test chat API with Postman/curl
2. Update frontend with Railway URL
3. Deploy frontend to Vercel
4. Celebrate! 🎊
