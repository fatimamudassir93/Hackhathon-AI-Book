# Quick Vercel Deployment Guide

## Overview

This is a streamlined guide for deploying to Vercel. For full deployment instructions including backend setup, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## Prerequisites

- GitHub repository with your code pushed
- Vercel account (free tier works)
- Backend API deployed and accessible (see DEPLOYMENT.md Part 1)

## Steps

### 1. Prepare Your Repository

Make sure your changes are committed and pushed:

```bash
git add .
git commit -m "feat: configure for Vercel deployment"
git push origin main
```

### 2. Import Project to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository
4. Authorize Vercel to access the repository

### 3. Configure Project Settings

**Framework Preset**: Docusaurus (auto-detected)

**Root Directory**: `physical-ai-book`

**Build & Development Settings**:
- Build Command: `npm run build` (auto-detected)
- Output Directory: `build` (auto-detected)
- Install Command: `npm install` (auto-detected)

### 4. Set Environment Variables

Click "Environment Variables" and add:

```
REACT_APP_API_URL
```

**Value**: Your backend URL (e.g., `https://your-backend.onrender.com`)

⚠️ **Critical**: Make sure this URL is your actual backend deployment URL, not localhost!

### 5. Deploy

1. Click "Deploy"
2. Wait for build to complete (2-5 minutes)
3. Click on the deployment URL to view your site

### 6. Update Backend CORS

After deployment, you need to allow your Vercel URL in the backend:

1. Go to your backend hosting (Render/Railway/etc.)
2. Add/update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
3. Redeploy the backend if needed

### 7. Test

1. Visit your Vercel URL
2. Open the chatbot (💬 button in bottom right)
3. Send a test message
4. Verify the response comes back

## Common Issues

### "Cannot connect to backend server"

**Cause**: Frontend can't reach the backend API

**Fix**:
1. Check `REACT_APP_API_URL` in Vercel environment variables
2. Make sure it's the actual backend URL (not localhost)
3. Verify backend is running
4. Redeploy frontend after changing env vars

### CORS Errors

**Cause**: Backend is blocking requests from your Vercel URL

**Fix**:
1. Add your Vercel URL to backend's `ALLOWED_ORIGINS`
2. Format: `https://your-app.vercel.app` (no trailing slash)
3. Redeploy backend

### Build Failures

**Cause**: TypeScript errors or missing dependencies

**Fix**:
1. Check build logs in Vercel dashboard
2. Make sure code builds locally: `npm run build`
3. Fix any TypeScript errors
4. Push fixes and Vercel will auto-redeploy

## Environment Variables in Vercel

### How to Add/Update

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Environment Variables"
3. Add or edit variables
4. Click "Save"
5. Redeploy for changes to take effect

### When to Use Each Environment

- **Production**: Live site (your-app.vercel.app)
- **Preview**: Pull request deployments
- **Development**: Local development (not used in Vercel)

For this project, add variables to **Production** and **Preview**.

## Custom Domain

### Add a Custom Domain

1. Go to Project Settings → Domains
2. Enter your domain name
3. Follow DNS configuration steps:
   - **Vercel DNS**: Transfer nameservers to Vercel
   - **External DNS**: Add A or CNAME records

4. Wait for DNS propagation (up to 48 hours)

### Update Backend CORS for Custom Domain

After adding a custom domain, update backend's `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://yourdomain.com,https://your-app.vercel.app
```

## Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **Push to `main`**: Deploys to production
- **Push to other branch**: Creates preview deployment
- **Pull request**: Creates preview deployment

### Disable Auto-Deploy

Project Settings → Git → "Ignored Build Step": Configure custom rules

## Monitoring

### View Logs

1. Go to Deployments
2. Click on a deployment
3. View build logs and runtime logs

### Analytics

Available in project dashboard (may require paid plan for detailed analytics)

## Rollback

If a deployment breaks your site:

1. Go to Deployments
2. Find the last working deployment
3. Click "..." → "Promote to Production"

## Next Steps

- [ ] Test all features (chat, auth, personalization)
- [ ] Set up custom domain
- [ ] Configure monitoring
- [ ] Review security settings
- [ ] Set up GitHub branch protection

## Support

- Vercel Docs: https://vercel.com/docs
- Docusaurus Docs: https://docusaurus.io/docs/deployment#deploying-to-vercel
- Project Issues: See [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section
