# Environment Variables Guide

## Quick Setup

1. Copy example file:

   ```bash
   cp .env.example .env
   ```

2. Generate SECRET_KEY:

   ```bash
   openssl rand -hex 32
   ```

3. Edit `.env` with your values

---

## Required Variables

### Database

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

### Naver Cloud Platform

Get keys from [Naver Cloud Console](https://www.ncloud.com/)

```bash
NAVER_API_KEY=your_api_key
NAVER_API_SECRET=your_api_secret
NAVER_APIGW_KEY=your_gateway_key
HYPERCLOVA_API_KEY=your_hyperclova_key
HYPERCLOVA_API_URL=https://clovastudio.apigw.ntruss.com/...
CLOVA_EMBEDDING_API_KEY=your_embedding_key
CLOVA_EMBEDDING_URL=https://clovastudio.apigw.ntruss.com/...
```

### Security

```bash
SECRET_KEY=your_32_char_random_string  # Use openssl rand -hex 32
```

### Optional Services

```bash
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

---

## Environment Examples

### Local Development

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://noteai_user:noteai_password@localhost:5432/noteai_db
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
```

### Docker Compose

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://noteai_user:noteai_password@postgres:5432/noteai_db
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
```

**Note:** Use service names (postgres, redis, qdrant) instead of localhost

### Production

```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql+asyncpg://prod_user:STRONG_PASSWORD@prod-db-host:5432/noteai_prod
SECRET_KEY=<64-character-random-string>
CORS_ORIGINS=https://yourdomain.com
```

---

## Security Best Practices

1. ✅ Never commit `.env` to git
2. ✅ Use strong SECRET_KEY (min 32 chars)
3. ✅ Rotate keys regularly in production
4. ✅ Different keys for dev/staging/prod
5. ✅ Enable HTTPS in production

---

## Testing Connection

```bash
# Test database
docker exec noteai_app python -c "from app.core.database import engine; print('DB OK')"

# Test Redis
docker exec noteai_redis redis-cli ping

# Test Qdrant
curl http://localhost:6333/collections
```
