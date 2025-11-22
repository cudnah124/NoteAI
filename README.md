# NoteAI Backend

AI-powered note-taking and document analysis system with RAG (Retrieval-Augmented Generation).

## 🌟 Features

- **Multi-source Document Processing**: PDF, DOCX, Images (instant processing)
- **AI-Powered Analysis**: HyperCLOVA X for intelligent note review with language detection
- **RAG (Retrieval-Augmented Generation)**: Context-aware Q&A using Qdrant vector DB
- **Real-time Chat**: Interactive Q&A with documents
- **Study Recommendations**: AI-powered learning suggestions
- **Production-Ready**: Railway deployment with PostgreSQL + Qdrant Cloud

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (Next.js)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  FastAPI App    │◄────►│  PostgreSQL DB   │
│  (Backend API)  │      │  (User/Docs)     │
│  Railway.app    │      │  Railway         │
└────────┬────────┘      └──────────────────┘
         │
         ├──────────────►┌──────────────────┐
         │               │  Qdrant Cloud    │
         │               │  (Vector Store)  │
         │               └──────────────────┘
         │
         └──────────────►┌──────────────────┐
                         │  Naver Cloud     │
                         │  HyperCLOVA X    │
                         └──────────────────┘
```

         │
         ├──────────────►┌──────────────────┐
         │               │  Redis Cache     │
         │               │  (Sessions)      │
         │               └──────────────────┘
         │
         └──────────────►┌──────────────────┐
                         │  Naver Cloud     │
                         │  - HyperCLOVA X  │
                         │  - Embeddings    │
                         │  - Speech API    │
                         └──────────────────┘

````

## 🚀 Quick Start

### Local Development

1. **Clone and setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
````

2. **Start services:**

   ```bash
   docker-compose up -d
   ```

3. **Access API:**
   - API: http://localhost:8000
   - Swagger docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Railway Deployment

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for complete guide.

**Quick steps:**

1. Push to GitHub
2. Connect Railway to your repo
3. Add PostgreSQL database
4. Set environment variables (see `.env.example`)
5. Deploy automatically

**Required services:**

- Railway PostgreSQL (auto-provisioned)
- Qdrant Cloud (vector database)
- Naver Cloud Platform (AI APIs)

## 📚 API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint reference.

### Chạy integration tests:

```bash
docker exec noteai_app python test_api.py
```

**Test coverage (10 test cases):**

- ✅ Authentication (register, login)
- ✅ Documents (upload, URL, status)
- ✅ Chat & RAG (sessions, messages, history)
- ✅ Notes (CRUD operations)
- ✅ AI Review (note analysis)
- ✅ Web URL documents
- ✅ YouTube documents
- ✅ Streaming chat
- ✅ Complete E2E workflow
- ✅ Full RAG workflow with streaming

### Test output:

```
Total: 10 | Passed: 10 | Failed: 0
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

Tất cả endpoints (trừ `/auth/*`) yêu cầu JWT token:

```http
Authorization: Bearer <token>
```

### Main Endpoints

#### 1. Auth

- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập (nhận token)

#### 2. Documents

- `POST /documents/upload` - Upload file (PDF, image)
- `POST /documents/url` - Xử lý URL (web, YouTube)
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document
- `GET /documents/{id}/status` - Check status
- `DELETE /documents/{id}` - Delete document

#### 3. Chat (RAG)

- `POST /chat/session` - Tạo chat session
- `POST /chat/message` - Gửi message (AI response)
- `GET /chat/session/{id}/messages` - Chat history
- `GET /chat/sessions` - List sessions
- `DELETE /chat/session/{id}` - Delete session

#### 4. Notes

- `POST /notes/` - Tạo note
- `GET /notes/` - List notes
- `GET /notes/{id}` - Get note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

#### 5. AI Services

- `POST /ai/review` - AI review note
- `GET /ai/recommend/{doc_id}` - Study recommendations

**Chi tiết:** Xem `API_DOCUMENTATION.md`

## 🔧 Development

### Project Structure

```
NoteAI/
├── app/
│   ├── core/           # Config, database, security
│   ├── features/       # Feature modules
│   │   ├── auth/
│   │   ├── documents/
│   │   ├── chat/
│   │   ├── notes/
│   │   └── ai/
│   ├── integrations/   # External services (Naver, Qdrant)
│   ├── models/         # SQLAlchemy models
│   └── schemas/        # Pydantic schemas
├── test_api.py         # Integration tests
├── docker-compose.yml
└── main.py             # Entry point
```

### Environment Variables

**Required:**

- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - JWT secret
- `NAVER_API_KEY`, `NAVER_API_SECRET`, `NAVER_APIGW_KEY`
- `HYPERCLOVA_API_KEY`, `HYPERCLOVA_API_URL`
- `CLOVA_EMBEDDING_API_KEY`, `CLOVA_EMBEDDING_URL`
- `QDRANT_URL`
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`

**Chi tiết:** Xem `ENV_GUIDE.md`

### Common Commands

**View logs:**

```bash
docker-compose logs -f app
```

**Restart app:**

```bash
docker-compose restart app
```

**Access app shell:**

```bash
docker exec -it noteai_app bash
```

**Access database:**

```bash
docker exec -it noteai_postgres psql -U noteai_user -d noteai_db
```

**Reset database:**

```bash
docker exec noteai_app python reset_db.py
```

**Stop all services:**

```bash
docker-compose down
```

**Stop and remove volumes:**

```bash
docker-compose down -v
```

## 🎯 Usage Example

### Python Client Example

```python
import httpx
import asyncio

async def main():
    BASE_URL = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Register & Login
        await client.post("/auth/register", json={
            "email": "user@test.com",
            "password": "Pass123!",
            "full_name": "Test User"
        })

        response = await client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "Pass123!"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload Document
        doc_response = await client.post("/documents/url",
            json={
                "type": "web",
                "source_url": "https://example.com/article"
            },
            headers=headers
        )
        doc_id = doc_response.json()["id"]

        # 3. Create Note
        note_response = await client.post("/notes/",
            json={
                "title": "My Study Notes",
                "content": "# Key Concepts\n- Point 1\n- Point 2",
                "document_id": doc_id
            },
            headers=headers
        )
        note_id = note_response.json()["id"]

        # 4. Chat with AI (RAG)
        session = await client.post("/chat/session",
            json={"document_id": doc_id},
            headers=headers
        )
        session_id = session.json()["id"]

        message = await client.post("/chat/message",
            json={
                "session_id": session_id,
                "content": "What are the main topics in this document?"
            },
            headers=headers
        )
        print(f"AI: {message.json()['content']}")

        # 5. AI Review
        review = await client.post("/ai/review",
            json={"note_id": note_id},
            headers=headers
        )
        print(f"Score: {review.json()['correctness_score']}/10")

asyncio.run(main())
```

### cURL Examples

**Register:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}'
```

**Login:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}'
```

**Upload Document:**

```bash
TOKEN="your_jwt_token"
curl -X POST http://localhost:8000/documents/url \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"web","source_url":"https://example.com"}'
```

**Chat Message:**

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"uuid","content":"What is this about?"}'
```

## 🔍 Troubleshooting

### App không start được

```bash
# Xem logs
docker-compose logs app

# Kiểm tra .env file
cat .env

# Restart services
docker-compose restart
```

### Database connection error

```bash
# Kiểm tra postgres
docker-compose ps postgres

# Test connection
docker exec noteai_postgres psql -U noteai_user -d noteai_db -c "SELECT 1"
```

### Test fails

```bash
# Reset database
docker exec noteai_app python reset_db.py

# Restart app
docker-compose restart app

# Chạy lại test
docker exec noteai_app python test_api.py
```

### Port conflicts

```bash
# Dừng services
docker-compose down

# Kiểm tra port đang dùng
netstat -ano | findstr "8000"
netstat -ano | findstr "5432"

# Đổi port trong docker-compose.yml nếu cần
```

## 🌐 Production Deployment

### Local vs Cloud

**Local Development:**

- Qdrant, PostgreSQL, Redis run in Docker
- No API keys needed for vector DB

**Production:**

- Use Qdrant Cloud for vector database
- Use managed PostgreSQL (Supabase, Railway, AWS RDS)
- Use managed Redis (Redis Cloud, Upstash)

### Deploy to Cloud

**See detailed guide:** [`DEPLOYMENT.md`](./DEPLOYMENT.md)

**Quick Setup:**

1. **Create Qdrant Cloud cluster** at https://cloud.qdrant.io/

2. **Update `.env` for production:**

   ```env
   # Qdrant Cloud
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=qdr_xxxxxxxxxxxxx

   # PostgreSQL Cloud
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db

   # Redis Cloud
   REDIS_URL=redis://default:pass@host:6379

   # Production settings
   ENVIRONMENT=production
   DEBUG=False
   MOCK_MODE=false
   ```

3. **Deploy app** to:
   - Azure Container Apps
   - AWS ECS Fargate
   - Google Cloud Run
   - Railway / Render / Fly.io

**Code already supports both!** Just set `QDRANT_API_KEY` to enable cloud mode.

## 📝 Notes

- **Test file:** `test_api.py` chứa 10 integration tests hoàn chỉnh
- **API docs:** Truy cập `/docs` để xem Swagger UI interactive
- **Database:** Auto-create tables khi start lần đầu
- **Vector DB:** Qdrant tự động tạo collections
- **Celery:** Background tasks cho document processing

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

MIT License

## 🆘 Support

- Documentation: `API_DOCUMENTATION.md`
- Environment: `ENV_GUIDE.md`
- Integration tests: `test_api.py`
