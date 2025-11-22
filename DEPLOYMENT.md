# NoteAI - Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Cloud Deployment (Recommended for Production)

#### 1. **Qdrant Cloud Setup**

```bash
# Sign up at https://cloud.qdrant.io/
# Create a new cluster
# Get your cluster URL and API key
```

Update `.env`:

```env
QDRANT_URL=https://xyz-abc-123.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-cloud-api-key-here
```

#### 2. **PostgreSQL Cloud** (e.g., Supabase, Railway, AWS RDS)

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

#### 3. **Redis Cloud** (e.g., Redis Cloud, Upstash)

```env
REDIS_URL=redis://default:password@host:port
```

#### 4. **Application Deployment**

**Option A: Docker Compose on VPS**

```bash
# 1. Copy docker-compose.yml to server
# 2. Update .env with cloud credentials
# 3. Run only the app services
docker-compose up -d app celery_worker celery_flower
```

**Option B: Container Platforms (Azure Container Apps, AWS ECS, Google Cloud Run)**

```bash
# Build and push image
docker build -t noteai:latest .
docker tag noteai:latest your-registry/noteai:latest
docker push your-registry/noteai:latest

# Deploy using platform-specific commands
```

**Option C: Kubernetes**

```bash
# Use kubernetes/ manifests (create if needed)
kubectl apply -f kubernetes/
```

---

### Option 2: Full Local Deployment (Development/Testing)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

---

## 🔧 Environment Variables for Production

### Required Services

| Service         | Local            | Cloud Alternative                            |
| --------------- | ---------------- | -------------------------------------------- |
| **PostgreSQL**  | Docker container | Supabase, Railway, Neon, AWS RDS             |
| **Redis**       | Docker container | Redis Cloud, Upstash, AWS ElastiCache        |
| **Qdrant**      | Docker container | Qdrant Cloud                                 |
| **Application** | Docker container | Azure Container Apps, AWS ECS, GCP Cloud Run |

### Configuration Matrix

```env
# ==============================================
# PRODUCTION CONFIGURATION
# ==============================================

# Database (Cloud)
DATABASE_URL=postgresql+asyncpg://user:pass@cloud-host:5432/noteai

# Redis (Cloud)
REDIS_URL=redis://default:pass@cloud-host:6379

# Qdrant (Cloud)
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-api-key

# Naver Cloud Platform (Always required)
NAVER_API_KEY=ncp_iam_xxx
NAVER_API_SECRET=ncp_iam_xxx
HYPERCLOVA_API_KEY=nv-xxx
CLOVA_EMBEDDING_API_KEY=nv-xxx

# Application
ENVIRONMENT=production
DEBUG=False
MOCK_MODE=false
```

---

## 📊 Qdrant Cloud Setup (Detailed)

### 1. Create Cluster

1. Go to https://cloud.qdrant.io/
2. Sign up / Log in
3. Click "Create Cluster"
4. Choose plan (Free tier available)
5. Select region closest to your app server

### 2. Get Credentials

```
Cluster URL: https://xyz-abc-123.qdrant.io:6333
API Key: qdr_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Update Configuration

```python
# app/integrations/vector_db/qdrant.py already supports this!
# Just set environment variables:

QDRANT_URL=https://xyz-abc-123.qdrant.io:6333
QDRANT_API_KEY=qdr_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Test Connection

```bash
docker exec noteai_app python -c "
from app.integrations.vector_db import vector_db
collections = vector_db.client.get_collections()
print(f'Connected to Qdrant Cloud: {len(collections.collections)} collections')
"
```

---

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Set `MOCK_MODE=false` in production
- [ ] Use HTTPS for all external services
- [ ] Enable CORS only for trusted domains
- [ ] Store secrets in secure vault (Azure Key Vault, AWS Secrets Manager)
- [ ] Use connection strings with SSL enabled
- [ ] Set up monitoring and logging (Sentry, DataDog)
- [ ] Configure rate limiting on API endpoints
- [ ] Enable authentication on all admin endpoints

---

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 3 # Multiple app instances

  celery_worker:
    deploy:
      replicas: 5 # Multiple workers for background tasks
```

### Database

- Use read replicas for scaling reads
- Connection pooling (already configured with SQLAlchemy)
- Consider sharding for very large datasets

### Vector Database (Qdrant)

- Qdrant Cloud handles scaling automatically
- For self-hosted: Use Qdrant distributed mode

### Caching

- Redis for session storage and caching
- Use CDN for static assets
- Implement response caching for expensive queries

---

## 🎯 Deployment Checklist

### Pre-Deployment

- [ ] Run all tests: `pytest`
- [ ] Check security: `bandit -r app/`
- [ ] Update dependencies: `pip-compile requirements.in`
- [ ] Build Docker image: `docker build -t noteai .`
- [ ] Tag with version: `docker tag noteai noteai:v1.0.0`

### Deployment

- [ ] Push to container registry
- [ ] Update environment variables on server
- [ ] Run database migrations
- [ ] Deploy new version
- [ ] Run smoke tests
- [ ] Monitor logs for errors

### Post-Deployment

- [ ] Verify all APIs are responding
- [ ] Check Qdrant connection and data
- [ ] Test critical user flows
- [ ] Monitor performance metrics
- [ ] Set up alerts for errors

---

## 🆘 Troubleshooting

### Qdrant Connection Issues

```bash
# Test cloud connection
curl https://your-cluster.qdrant.io:6333/collections \
  -H "api-key: your-api-key"

# Check app logs
docker logs noteai_app | grep -i qdrant
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec noteai_app python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connected!')
"
```

### Naver API Issues

```bash
# Check API keys are set
docker exec noteai_app env | grep NAVER
docker exec noteai_app env | grep HYPERCLOVA
docker exec noteai_app env | grep CLOVA_EMBEDDING
```

---

## 🌐 Recommended Cloud Platforms

### All-in-One Platforms

- **Railway** - Easy deployment, includes DB + Redis
- **Render** - Similar to Railway, good free tier
- **Fly.io** - Global edge deployment

### Container Platforms

- **Azure Container Apps** - Serverless containers
- **AWS ECS Fargate** - Managed containers
- **Google Cloud Run** - Serverless containers

### Database/Vector DB

- **Qdrant Cloud** - Managed vector database
- **Supabase** - PostgreSQL with great dashboard
- **Upstash** - Serverless Redis

---

## 📞 Support

For deployment issues:

1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Naver Cloud Platform status
4. Check Qdrant Cloud status
5. Open issue on GitHub

---

**Last Updated**: November 2025
**Version**: 1.0.0
