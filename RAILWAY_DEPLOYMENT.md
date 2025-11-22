# Railway Deployment Guide

## Prerequisites

1. Railway account
2. PostgreSQL database on Railway
3. Qdrant Cloud account (or Qdrant instance)
4. Naver Cloud Platform API keys

## Environment Variables

Set these in Railway dashboard:

### Database

```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### JWT Authentication

```
SECRET_KEY=your-secret-key-here-minimum-32-characters
```

### Naver Cloud Platform

```
NCP_CLOVASTUDIO_API_KEY=your-naver-api-key
NCP_CLOVASTUDIO_API_KEY_PRIMARY_VAL=your-primary-key
NCP_CLOVASTUDIO_REQUEST_ID=your-request-id
```

### Qdrant Vector Database

```
QDRANT_URL=https://your-qdrant-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
```

### App Configuration

```
MOCK_MODE=false
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
PORT=8000
```

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Connect Railway to GitHub

1. Go to [Railway Dashboard](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Dockerfile

### 3. Configure Environment Variables

In Railway dashboard:

1. Go to your project
2. Click "Variables" tab
3. Add all environment variables listed above
4. Click "Deploy"

### 4. Set up PostgreSQL

Railway automatically provisions PostgreSQL:

1. Click "New" → "Database" → "PostgreSQL"
2. Railway will set `DATABASE_URL` automatically
3. Database tables will be created on first run

### 5. Configure Custom Domain (Optional)

1. Go to "Settings" tab
2. Click "Generate Domain" for Railway subdomain
3. Or add your custom domain

## File Structure

```
NoteAI/
├── app/                    # Application code
│   ├── core/              # Core configs
│   ├── features/          # Feature modules
│   ├── integrations/      # External integrations
│   ├── models/            # Database models
│   └── schemas/           # Pydantic schemas
├── main.py                # FastAPI entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── railway.json          # Railway config
├── Procfile              # Alternative start command
└── .env.example          # Environment template

```

## Health Check

After deployment, check:

```bash
curl https://your-app.railway.app/
# Should return: {"message": "NoteAI API"}

curl https://your-app.railway.app/health
# Should return: {"status": "healthy", "database": "connected"}
```

## Monitoring

Railway provides:

- Real-time logs
- Metrics (CPU, Memory, Network)
- Deployment history
- Auto-restarts on failure

Access via Railway dashboard.

## Troubleshooting

### Database Connection Issues

Check `DATABASE_URL` format:

```
postgresql://user:password@host:port/dbname
```

### Port Issues

Railway uses `$PORT` environment variable. Dockerfile is configured to use it automatically.

### CORS Issues

Update `ALLOWED_ORIGINS` environment variable with your frontend URLs.

### API Key Issues

Verify all Naver Cloud Platform keys are set correctly:

- `NCP_CLOVASTUDIO_API_KEY`
- `NCP_CLOVASTUDIO_API_KEY_PRIMARY_VAL`
- `NCP_CLOVASTUDIO_REQUEST_ID`

## Scaling

Railway auto-scales based on:

- CPU usage
- Memory usage
- Request volume

Configure in Settings → Autoscaling.

## CI/CD

Railway automatically deploys on push to main branch. To disable:

1. Go to Settings
2. Toggle "Auto Deploy" off

## Cost Optimization

- Use Railway's free tier for development
- Upgrade to Hobby ($5/month) for production
- Monitor usage in dashboard
- Set spending limits in billing settings

## Security Checklist

- ✅ All secrets in environment variables
- ✅ `.env` file in `.gitignore`
- ✅ CORS configured properly
- ✅ JWT secret key is strong (32+ chars)
- ✅ Database has strong password
- ✅ HTTPS enabled (automatic on Railway)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project API Docs: https://your-app.railway.app/docs
