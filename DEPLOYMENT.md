# Deployment Guide

This guide explains how to deploy the Physical AI Book application to production.

## Architecture Overview

The application consists of two main components:
- **Frontend**: Docusaurus-based documentation site (deployed to Vercel)
- **Backend**: FastAPI RAG service (deployed separately to Render/Railway/etc.)

## Prerequisites

1. GitHub account
2. Vercel account (for frontend)
3. Render/Railway/Vercel account (for backend)
4. API keys for:
   - Groq/Gemini/OpenAI (LLM provider)
   - Qdrant (vector database)
   - Neon (PostgreSQL database)

## Part 1: Deploy Backend (FastAPI)

### Option A: Deploy to Render (Recommended)

1. **Create a new Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `rag-backend` directory as the root

2. **Configure Build Settings**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables** (in Render dashboard)
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   QDRANT_HOST=https://your-qdrant-instance.cloud.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=postgresql://user:pass@host/db
   AUTH_SECRET=your-secret-key-minimum-32-characters-long
   LLM_PRIORITY=groq,gemini,openai,ollama
   ALLOWED_ORIGINS=https://your-frontend-vercel-app.vercel.app
   ```

4. **Deploy**
   - Render will automatically deploy your backend
   - Note the deployment URL (e.g., `https://your-backend.onrender.com`)

### Option B: Deploy to Railway

1. **Create a new project on Railway**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure the service**
   - Set root directory to `rag-backend`
   - Railway auto-detects Python and installs dependencies

3. **Add Environment Variables** (same as Render above)

4. **Deploy**
   - Railway will automatically deploy
   - Note the deployment URL

### Option C: Deploy to Vercel (Serverless)

⚠️ **Note**: This requires adapting the FastAPI app to work with Vercel's serverless functions.

1. Create `rag-backend/vercel.json`:
   ```json
   {
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

2. Update `main.py` to export the app for Vercel:
   ```python
   # At the end of main.py
   # For Vercel deployment
   handler = app
   ```

3. Deploy via Vercel CLI or GitHub integration

## Part 2: Deploy Frontend (Docusaurus)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "feat: configure deployment"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import your GitHub repository

3. **Configure Project**
   - **Framework Preset**: Docusaurus
   - **Root Directory**: `physical-ai-book`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

4. **Set Environment Variables** (in Vercel dashboard)

   Go to Project Settings → Environment Variables:

   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```

   ⚠️ **Important**: Replace `https://your-backend.onrender.com` with your actual backend URL from Part 1

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Note the deployment URL (e.g., `https://your-app.vercel.app`)

## Part 3: Connect Frontend and Backend

1. **Update Backend CORS Configuration**

   In your backend deployment (Render/Railway/Vercel), update the `ALLOWED_ORIGINS` environment variable:

   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
   ```

   You can specify multiple origins separated by commas.

2. **Redeploy Backend** (if needed)
   - Most platforms auto-redeploy when you update environment variables
   - If not, trigger a manual redeploy

3. **Test the Connection**
   - Visit your Vercel frontend URL
   - Open the chatbot
   - Try sending a message
   - Check browser console for any CORS errors

## Part 4: Custom Domain (Optional)

### Frontend Domain

1. In Vercel project settings:
   - Go to "Domains"
   - Add your custom domain
   - Follow DNS configuration instructions

2. Update backend CORS:
   ```
   ALLOWED_ORIGINS=https://your-custom-domain.com
   ```

### Backend Domain

1. In Render/Railway settings:
   - Add custom domain
   - Configure DNS

2. Update frontend environment variable:
   ```
   REACT_APP_API_URL=https://api.your-custom-domain.com
   ```

## Security Checklist

- [ ] Rotate all API keys from `.env` file (they may be exposed)
- [ ] Set strong `AUTH_SECRET` (32+ characters)
- [ ] Configure specific `ALLOWED_ORIGINS` (don't use `*` in production)
- [ ] Enable HTTPS for all services
- [ ] Never commit `.env` files to git
- [ ] Use environment variables for all secrets
- [ ] Review and update Qdrant and Neon access controls

## Environment Variables Reference

### Frontend (`physical-ai-book`)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.example.com` |

### Backend (`rag-backend`)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | Yes* | Groq API key | `gsk_xxx...` |
| `GEMINI_API_KEY` | Yes* | Google Gemini API key | `AIza...` |
| `OPENAI_API_KEY` | No | OpenAI API key | `sk-...` |
| `QDRANT_HOST` | Yes | Qdrant cluster URL | `https://xxx.cloud.qdrant.io` |
| `QDRANT_API_KEY` | Yes | Qdrant API key | `xxx...` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://...` |
| `AUTH_SECRET` | Yes | JWT signing secret | 32+ random characters |
| `LLM_PRIORITY` | No | LLM provider priority | `groq,gemini,openai,ollama` |
| `ALLOWED_ORIGINS` | Yes | CORS allowed origins | `https://app.vercel.app` |

\* At least one LLM provider API key is required

## Troubleshooting

### Frontend can't connect to backend

**Symptoms**: Chat returns "Cannot connect to backend server"

**Solutions**:
1. Check that `REACT_APP_API_URL` is set correctly in Vercel
2. Verify backend is running and accessible
3. Check browser console for CORS errors
4. Ensure `ALLOWED_ORIGINS` includes your frontend URL

### CORS errors in browser console

**Symptoms**: "Access-Control-Allow-Origin" errors

**Solutions**:
1. Add your frontend URL to backend's `ALLOWED_ORIGINS`
2. Ensure `allow_credentials=True` in backend CORS config
3. Redeploy backend after updating environment variables

### Authentication fails

**Symptoms**: Users can't sign in/up

**Solutions**:
1. Check `DATABASE_URL` is correct
2. Verify `AUTH_SECRET` is set
3. Check backend logs for database connection errors

### Chat queries fail

**Symptoms**: Chat returns errors or empty responses

**Solutions**:
1. Verify Qdrant connection (check `QDRANT_HOST` and `QDRANT_API_KEY`)
2. Ensure LLM API keys are valid
3. Check backend logs for specific errors

## Monitoring

### Frontend (Vercel)

- Check deployment logs in Vercel dashboard
- Monitor function invocations and errors
- Review Analytics for performance metrics

### Backend (Render/Railway)

- Check application logs for errors
- Monitor resource usage (CPU, memory)
- Set up health check endpoints
- Configure alerts for downtime

## Rollback Procedure

### Frontend

1. Go to Vercel dashboard → Deployments
2. Find the last working deployment
3. Click "..." → "Promote to Production"

### Backend

1. Go to Render/Railway dashboard
2. Navigate to deployment history
3. Rollback to previous deployment

## CI/CD

Both Vercel and Render/Railway support automatic deployments:

- **Frontend**: Auto-deploys on push to `main` branch
- **Backend**: Auto-deploys on push to `main` branch

To disable:
- Vercel: Project Settings → Git → Disable auto-deploy
- Render/Railway: Service Settings → Auto-Deploy → Off

## Support

If you encounter issues:
1. Check application logs
2. Review this documentation
3. Check environment variable configuration
4. Verify all services are running
5. Test locally first before deploying

## Next Steps

After successful deployment:
1. Test all features (chat, auth, personalization)
2. Set up monitoring and alerts
3. Configure custom domains
4. Set up backup procedures for database
5. Document any custom configuration
