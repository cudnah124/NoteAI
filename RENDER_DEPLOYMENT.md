# Render Deployment Guide

## Prerequisites

1. Render account (https://render.com)
2. PostgreSQL database on Render
3. Qdrant Cloud account
4. Naver Cloud Platform API keys

## Deployment Steps

### 1. Create Web Service

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: noteai-backend
   - **Environment**: Docker
   - **Branch**: main
   - **Plan**: Starter ($7/month) or Free

### 2. Add PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: noteai-db
3. Plan: Starter or Free
4. Copy **Internal Database URL**

### 3. Environment Variables

In Web Service → Environment tab, add:

```bash
# Database (use Internal Database URL from Render PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Naver Cloud Platform
NCP_CLOVASTUDIO_API_KEY=<your-key>
NCP_CLOVASTUDIO_API_KEY_PRIMARY_VAL=<your-key>
NCP_CLOVASTUDIO_REQUEST_ID=<your-id>

# Qdrant Cloud
QDRANT_URL=https://<cluster>.qdrant.io
QDRANT_API_KEY=<your-key>

# App Config
MOCK_MODE=false
ALLOWED_ORIGINS=https://your-frontend.vercel.app
PORT=10000
```

### 4. Build Configuration

Render auto-detects `Dockerfile`. Build command:
```bash
docker build -t noteai .
```

Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 5. Deploy

Click "Manual Deploy" or push to GitHub (auto-deploy).

## Key Differences from Railway

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | $5 credit/month | 750 hours/month |
| PostgreSQL | Included | Separate service |
| Auto Deploy | Yes | Yes |
| Custom Domain | Free | Free |
| Build Time | Fast | Medium |
| Cold Start | Minimal | 1-2 minutes (Free tier) |

## Render-Specific Files

No additional files needed! Render uses:
- ✅ `Dockerfile` (already configured)
- ✅ `requirements.txt` (already present)

## Health Check Endpoint

Render checks: `https://your-app.onrender.com/health`

Ensure your FastAPI has this endpoint (already implemented).

## Custom Domain

1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records as instructed

## Monitoring

Render provides:
- Real-time logs
- Metrics dashboard
- Uptime monitoring
- Email alerts

## Troubleshooting

### Database Connection Error: "Name or service not known"

**Cause**: DATABASE_URL not set or incorrect format.

**Solution**:
1. Go to Render Dashboard → PostgreSQL service
2. Copy **Internal Database URL** (NOT External)
3. Go to Web Service → Environment
4. Add/Update `DATABASE_URL` with the copied URL
5. **Important**: Use the URL as-is (Render format: `postgresql://...`)
   - Don't add `postgresql+asyncpg://` prefix
   - The app handles the conversion automatically

**Format should be:**
```
postgresql://user:password@hostname/database
```

**Example:**
```
postgresql://noteai_user:abcd1234@dpg-xxxxx-a.oregon-postgres.render.com/noteai_db
```

### Database Connection Steps

1. **Create PostgreSQL first:**
   - New + → PostgreSQL
   - Name: noteai-db
   - Wait for "Available" status

2. **Get connection string:**
   - Click on noteai-db
   - Copy "Internal Database URL"

3. **Set in Web Service:**
   - Go to noteai-backend → Environment
   - Add `DATABASE_URL=<paste-internal-url>`
   - Save Changes

4. **Redeploy:**
   - Manual Deploy → Deploy latest commit

### Cold Starts (Free Tier)
Free tier spins down after 15 minutes of inactivity. First request takes 1-2 minutes.

**Solution**: Upgrade to Starter ($7/month) for always-on.

### Database Connection
Use **Internal Database URL** (not External) for better performance.

### Port Configuration
Render sets `PORT` environment variable. Dockerfile already handles this with `${PORT:-8000}`.

### Build Timeout
If build takes >15 minutes, optimize:
```dockerfile
# Cache pip packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

## Cost Comparison

**Render Free Tier:**
- 750 hours/month web service
- Free PostgreSQL (90 days, then $7/month)
- Cold starts after 15 min inactivity

**Render Starter ($7/month):**
- Always-on (no cold starts)
- Better performance
- Priority support

**Railway:**
- $5 credit/month (usually enough for small apps)
- Pay-as-you-go
- No cold starts

## Recommendation

- **Render Free**: Good for testing/portfolio projects
- **Render Starter ($7)**: Good for production if budget-conscious
- **Railway**: Best overall (simpler, faster, better DX)

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Status: https://status.render.com
