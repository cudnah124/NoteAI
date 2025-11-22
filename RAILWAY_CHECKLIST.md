# Railway Deployment Checklist

## ✅ Pre-Deployment

### Code Preparation

- [x] Remove all test files (`test_*.py`)
- [x] Remove development scripts (`reset_db.py`, `start.bat`, `start.sh`)
- [x] Update `.gitignore` for production
- [x] Create `.dockerignore` for optimized builds
- [x] Update Dockerfile for Railway compatibility (`$PORT` support)
- [x] Create `railway.json` configuration
- [x] Create `Procfile` for alternative deployment
- [x] Update `.env.example` with Railway-specific configs
- [x] Update README.md with deployment info

### Documentation

- [x] Create RAILWAY_DEPLOYMENT.md guide
- [x] Update API_DOCUMENTATION.md (complete)
- [x] Document environment variables

## 🔑 Environment Variables Setup

### Railway Dashboard → Variables Tab

**Database (Auto-configured by Railway):**

```
DATABASE_URL=postgresql://... (Railway sets this automatically)
```

**Security:**

```
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Naver Cloud Platform:**

```
NCP_CLOVASTUDIO_API_KEY=<your-api-key>
NCP_CLOVASTUDIO_API_KEY_PRIMARY_VAL=<your-primary-key>
NCP_CLOVASTUDIO_REQUEST_ID=<your-request-id>
```

**Qdrant Cloud:**

```
QDRANT_URL=https://<your-cluster>.qdrant.io
QDRANT_API_KEY=<your-api-key>
```

**Application:**

```
MOCK_MODE=false
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://another-domain.com
PORT=8000 (Railway sets automatically)
```

## 📦 External Services Setup

### 1. Qdrant Cloud

- [ ] Sign up at https://cloud.qdrant.io
- [ ] Create a cluster
- [ ] Get cluster URL and API key
- [ ] Add to Railway environment variables

### 2. Naver Cloud Platform

- [ ] Access https://console.ncloud.com/
- [ ] Enable CLOVA Studio
- [ ] Get API keys
- [ ] Add to Railway environment variables

### 3. Railway Database

- [ ] Add PostgreSQL from Railway dashboard
- [ ] DATABASE_URL will be set automatically
- [ ] Database tables auto-created on first run

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Railway Setup

- [ ] Login to https://railway.app
- [ ] New Project → Deploy from GitHub
- [ ] Select repository
- [ ] Railway detects Dockerfile automatically

### 3. Configure Services

- [ ] Add PostgreSQL database
- [ ] Set all environment variables
- [ ] Click "Deploy"

### 4. Verify Deployment

- [ ] Check deployment logs
- [ ] Test health endpoint: `https://your-app.railway.app/health`
- [ ] Test API docs: `https://your-app.railway.app/docs`
- [ ] Test authentication: Register + Login
- [ ] Test file upload
- [ ] Test chat functionality

## 🔍 Post-Deployment Verification

### Health Checks

```bash
# API Health
curl https://your-app.railway.app/
# Response: {"message": "NoteAI API"}

# Database Connection
curl https://your-app.railway.app/health
# Response: {"status": "healthy", "database": "connected"}

# API Documentation
curl https://your-app.railway.app/docs
# Should return Swagger UI HTML
```

### Functional Tests

- [ ] User registration works
- [ ] User login returns JWT token
- [ ] Document upload processes files
- [ ] Chat system connects to documents
- [ ] AI review responds in correct language
- [ ] Recommendations generate successfully

## ⚠️ Common Issues

### Issue: Database Connection Failed

**Solution:** Check DATABASE_URL format - Railway uses `postgresql://` (not `postgresql+asyncpg://`)

### Issue: Port Binding Error

**Solution:** Dockerfile now uses `${PORT:-8000}` - Railway sets $PORT automatically

### Issue: CORS Errors

**Solution:** Update ALLOWED_ORIGINS with your frontend URLs

### Issue: API Keys Not Working

**Solution:** Verify all Naver Cloud keys are copied correctly (no extra spaces)

### Issue: Qdrant Connection Failed

**Solution:** Ensure QDRANT_URL uses HTTPS and includes API key

## 📊 Monitoring

### Railway Dashboard

- [ ] Check deployment status
- [ ] Monitor logs (real-time)
- [ ] Review metrics (CPU, Memory, Network)
- [ ] Set up alerts

### Application Logs

```bash
# View logs from Railway CLI
railway logs

# Or from dashboard: Deployments → View Logs
```

## 🎯 Production Checklist

- [ ] All environment variables set correctly
- [ ] Database connected and tables created
- [ ] CORS configured for production domains
- [ ] MOCK_MODE set to false
- [ ] JWT SECRET_KEY is strong (32+ characters)
- [ ] API documentation accessible
- [ ] Health checks passing
- [ ] File upload works
- [ ] Chat functionality operational
- [ ] AI services responding correctly

## 🔐 Security Review

- [ ] `.env` file NOT in git
- [ ] All secrets in environment variables
- [ ] HTTPS enabled (automatic on Railway)
- [ ] CORS properly configured
- [ ] JWT secret is production-grade
- [ ] Database credentials secure
- [ ] API keys not exposed in code

## 📈 Scaling (Optional)

- [ ] Review Railway pricing plans
- [ ] Set up auto-scaling rules
- [ ] Configure resource limits
- [ ] Monitor usage and costs

## ✨ Deployment Complete!

Your NoteAI backend is now live on Railway! 🎉

**Next steps:**

1. Update frontend with new API URL
2. Test all features end-to-end
3. Monitor logs for any errors
4. Set up domain (optional)
5. Configure CI/CD for auto-deploy

**Support:**

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: https://github.com/your-repo/issues
