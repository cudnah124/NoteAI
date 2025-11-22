# NoteAI Backend API

AI-powered note-taking and document analysis system with RAG (Retrieval-Augmented Generation).

**Base URL (Production)**: `https://your-app.railway.app`  
**Base URL (Local)**: `http://localhost:8000`

---

## 📚 Quick Start for Frontend Developers

### 1. Authentication Flow

All endpoints (except `/auth/*`) require JWT token in header:
```http
Authorization: Bearer <your-jwt-token>
```

**Register User:**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

Response: { "id": "uuid", "email": "...", ... }
```

**Login:**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response: { "access_token": "eyJhbGc...", "token_type": "bearer" }
```

**Token expires in 30 minutes** - store it and use in all subsequent requests.

---

## 🌟 Core Features

- **Multi-format Document Processing**: PDF, DOCX (instant processing, 0.0s)
- **AI-Powered Note Review**: HyperCLOVA X with automatic language detection (Vietnamese/English)
- **RAG Chat System**: Context-aware Q&A with your documents
- **Study Recommendations**: AI analyzes your notes and suggests what to study next
- **Notes Management**: Full CRUD for markdown notes linked to documents

---

## 📖 API Endpoints Overview

### 🔐 Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new account | ❌ |
| POST | `/auth/login` | Get JWT token | ❌ |

---

### 📄 Documents (`/documents`, `/files`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/files/upload/document` | Upload PDF/DOCX (frontend-compatible) | ✅ |
| POST | `/documents/upload` | Upload file (alternative) | ✅ |
| POST | `/documents/url` | Process web URL/YouTube | ✅ |
| GET | `/documents/` | List all documents | ✅ |
| GET | `/documents/{id}` | Get document details | ✅ |
| GET | `/documents/{id}/status` | Check processing status | ✅ |
| DELETE | `/documents/{id}` | Delete document | ✅ |

**Frontend-compatible endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/files/metadata/document` | List documents with etag format |
| GET | `/files/metadata/note` | List notes with etag format |
| GET | `/files/metadata/note/{etag}` | Get note metadata by etag |
| GET | `/files/content/note/{etag}` | Get raw markdown content |

---

### 📝 Notes (`/notes`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/notes/` | Create new note | ✅ |
| GET | `/notes/` | List all notes | ✅ |
| GET | `/notes/{id}` | Get specific note | ✅ |
| PUT | `/notes/{id}` | Update note | ✅ |
| DELETE | `/notes/{id}` | Delete note | ✅ |

---

### 💬 Chat (`/chat`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chat/session` | Create chat session | ✅ |
| POST | `/chat/message` | Send message (RAG Q&A) | ✅ |
| GET | `/chat/session/{id}/messages` | Get chat history | ✅ |
| GET | `/chat/sessions` | List all sessions | ✅ |
| DELETE | `/chat/session/{id}` | Delete session | ✅ |

---

### 🤖 AI Services (`/ai`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/ai/review` | Review note with AI | ✅ |
| GET | `/ai/recommendations/{document_id}` | Get study recommendations | ✅ |

**✨ AI Features:**
- **Language Detection**: Automatically detects Vietnamese/English from note content
- **Multilingual Responses**: AI responds in same language as your note
- **Smart Review**: Provides strengths, improvements, corrections, and suggestions
- **Study Planning**: Analyzes coverage and recommends what to learn next

---

## 🔥 Common Use Cases

### Use Case 1: Upload & Process Document

```javascript
// 1. Upload document
const formData = new FormData();
formData.append('file', pdfFile);

const uploadRes = await fetch('https://api.example.com/files/upload/document', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

const { document } = await uploadRes.json();
// Response: { success: true, document: { id, etag, type, status, ... } }

// 2. Check processing status (optional - files process instantly)
const statusRes = await fetch(`https://api.example.com/documents/${document.id}/status`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

const status = await statusRes.json();
// Response: { id, status: "completed", progress_percentage: 100 }
```

---

### Use Case 2: Chat with Document

```javascript
// 1. Create chat session
const sessionRes = await fetch('https://api.example.com/chat/session', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ document_id: documentId })
});

const { id: sessionId } = await sessionRes.json();

// 2. Send message
const messageRes = await fetch('https://api.example.com/chat/message', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: sessionId,
    content: "What is this document about?"
  })
});

const aiResponse = await messageRes.json();
// Response: { id, session_id, content: "AI answer...", role: "assistant", ... }
```

---

### Use Case 3: Create & Review Note

```javascript
// 1. Create note
const noteRes = await fetch('https://api.example.com/notes/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: "Machine Learning Notes",
    content: "# Supervised Learning\n\n...",
    document_id: documentId
  })
});

const note = await noteRes.json();

// 2. Get AI review (detects language automatically)
const reviewRes = await fetch('https://api.example.com/ai/review', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ note_id: note.id })
});

const review = await reviewRes.json();
// Response: {
//   overall_feedback: "Ghi chú tốt...",
//   strengths: ["...", "..."],
//   areas_for_improvement: ["...", "..."],
//   specific_corrections: ["..."],
//   suggestions_for_expansion: ["..."]
// }
```

---

### Use Case 4: Get Study Recommendations

```javascript
const recsRes = await fetch(`https://api.example.com/ai/recommendations/${documentId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

const recommendations = await recsRes.json();
// Response: {
//   missing_sections: ["Chapter 5", "Section 3.2"],
//   key_concepts_to_review: ["Backpropagation", "CNN"],
//   coverage_percentage: 65,
//   overall_recommendation: "Focus on neural networks..."
// }
```

---

## 🎯 Response Formats

### Success Response
```json
{
  "id": "uuid",
  "field1": "value",
  "created_at": "2025-11-22T10:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content (delete success)
- `400` - Bad Request
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

---

## 🔧 Environment Setup

Frontend needs to set base URL:

```javascript
// .env.local
NEXT_PUBLIC_API_URL=https://your-app.railway.app

// Usage
const API_URL = process.env.NEXT_PUBLIC_API_URL;
fetch(`${API_URL}/auth/login`, { ... });
```

---

## 📊 CORS Configuration

Backend allows these origins (configured via `ALLOWED_ORIGINS` env variable):
- `http://localhost:3000` (Next.js dev)
- `http://localhost:5173` (Vite dev)
- Your production frontend domain

If you get CORS errors, ask backend team to add your domain to `ALLOWED_ORIGINS`.

---

## 🚀 Deployment

**Backend**: Railway (https://railway.app)  
**Database**: PostgreSQL (Railway)  
**Vector DB**: Qdrant Cloud  
**AI Provider**: Naver HyperCLOVA X

See detailed guides:
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Railway deployment
- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Render deployment
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference

---

## 📖 Full Documentation

- **Interactive API Docs**: `https://your-api.railway.app/docs` (Swagger UI)
- **Alternative Docs**: `https://your-api.railway.app/redoc` (ReDoc)
- **Complete Reference**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

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

```

---

## 💡 Tips for Frontend Developers

### Token Management
```javascript
// Store token after login
localStorage.setItem('token', response.access_token);

// Use in requests
const token = localStorage.getItem('token');
fetch(url, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Handle 401 (expired token)
if (response.status === 401) {
  localStorage.removeItem('token');
  router.push('/login');
}
```

### Error Handling
```javascript
try {
  const res = await fetch(url, options);
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Request failed');
  }
  return await res.json();
} catch (error) {
  console.error('API Error:', error.message);
  // Show toast notification
}
```

### File Upload with Progress
```javascript
const formData = new FormData();
formData.append('file', file);

const xhr = new XMLHttpRequest();
xhr.upload.onprogress = (e) => {
  const percent = (e.loaded / e.total) * 100;
  setProgress(percent);
};

xhr.open('POST', `${API_URL}/files/upload/document`);
xhr.setRequestHeader('Authorization', `Bearer ${token}`);
xhr.send(formData);
```

### Language Detection (Automatic)
```javascript
// Just send your note content - AI detects language automatically
const note = {
  title: "Học máy",
  content: "# Supervised Learning\n\nHọc có giám sát là..."
};

// AI will respond in Vietnamese because content is Vietnamese
const review = await fetch(`${API_URL}/ai/review`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ note_id: noteId })
});

// Response will be: { overall_feedback: "Ghi chú của bạn...", ... }
```

---

## 🐛 Common Issues

### CORS Error
**Problem**: `Access-Control-Allow-Origin` error  
**Solution**: Contact backend team to add your domain to `ALLOWED_ORIGINS`

### 401 Unauthorized
**Problem**: Token expired or invalid  
**Solution**: Login again to get new token (tokens expire after 30 minutes)

### File Upload Failed
**Problem**: File size too large  
**Solution**: Files must be < 10MB. Compress large PDFs before upload.

### Chat Not Working
**Problem**: Document not yet processed  
**Solution**: Check document status with `GET /documents/{id}/status` - wait for `status: "completed"`

---

## 📞 Support

- **API Documentation**: `https://your-api.railway.app/docs`
- **Complete Reference**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Backend Issues**: Open issue on GitHub
- **Deployment Help**: See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

---

## ⚡ Performance Notes

- **Document Processing**: Instant (0.0s for PDF/DOCX)
- **AI Review**: 2-5 seconds
- **Chat Response**: 1-3 seconds
- **Recommendations**: 2-4 seconds

All endpoints are async and optimized for production use.

---

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
