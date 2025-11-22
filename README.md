# NoteAI Backend API

AI-powered note-taking and document analysis system with RAG (Retrieval-Augmented Generation).

**Base URL**: `https://noteai-kbsb.onrender.com/`

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

| Method | Endpoint         | Description        | Auth Required |
| ------ | ---------------- | ------------------ | ------------- |
| POST   | `/auth/register` | Create new account | ❌            |
| POST   | `/auth/login`    | Get JWT token      | ❌            |

---

### 📄 Documents (`/documents`, `/files`)

| Method | Endpoint                 | Description                           | Auth Required |
| ------ | ------------------------ | ------------------------------------- | ------------- |
| POST   | `/files/upload/document` | Upload PDF/DOCX (frontend-compatible) | ✅            |
| POST   | `/documents/upload`      | Upload file (alternative)             | ✅            |
| POST   | `/documents/url`         | Process web URL/YouTube               | ✅            |
| GET    | `/documents/`            | List all documents                    | ✅            |
| GET    | `/documents/{id}`        | Get document details                  | ✅            |
| GET    | `/documents/{id}/status` | Check processing status               | ✅            |
| DELETE | `/documents/{id}`        | Delete document                       | ✅            |

**Frontend-compatible endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/files/metadata/document` | List documents with etag format |
| GET | `/files/metadata/note` | List notes with etag format |
| GET | `/files/metadata/note/{etag}` | Get note metadata by etag |
| GET | `/files/content/note/{etag}` | Get raw markdown content |

---

### 📝 Notes (`/notes`)

| Method | Endpoint      | Description       | Auth Required |
| ------ | ------------- | ----------------- | ------------- |
| POST   | `/notes/`     | Create new note   | ✅            |
| GET    | `/notes/`     | List all notes    | ✅            |
| GET    | `/notes/{id}` | Get specific note | ✅            |
| PUT    | `/notes/{id}` | Update note       | ✅            |
| DELETE | `/notes/{id}` | Delete note       | ✅            |

---

### 💬 Chat (`/chat`)

| Method | Endpoint                      | Description            | Auth Required |
| ------ | ----------------------------- | ---------------------- | ------------- |
| POST   | `/chat/session`               | Create chat session    | ✅            |
| POST   | `/chat/message`               | Send message (RAG Q&A) | ✅            |
| GET    | `/chat/session/{id}/messages` | Get chat history       | ✅            |
| GET    | `/chat/sessions`              | List all sessions      | ✅            |
| DELETE | `/chat/session/{id}`          | Delete session         | ✅            |

---

### 🤖 AI Services (`/ai`)

| Method | Endpoint                            | Description               | Auth Required |
| ------ | ----------------------------------- | ------------------------- | ------------- |
| POST   | `/ai/review`                        | Review note with AI       | ✅            |
| GET    | `/ai/recommendations/{document_id}` | Get study recommendations | ✅            |

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
formData.append("file", pdfFile);

const uploadRes = await fetch(
  "https://noteai-kbsb.onrender.com/files/upload/document",
  {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  }
);

const { document } = await uploadRes.json();
// Response: { success: true, document: { id, etag, type, status, ... } }

// 2. Check processing status (optional - files process instantly)
const statusRes = await fetch(
  `https://noteai-kbsb.onrender.com/documents/${document.id}/status`,
  {
    headers: { Authorization: `Bearer ${token}` },
  }
);

const status = await statusRes.json();
// Response: { id, status: "completed", progress_percentage: 100 }
```

---

### Use Case 2: Chat with Document

```javascript
// 1. Create chat session
const sessionRes = await fetch(
  "https://noteai-kbsb.onrender.com/chat/session",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ document_id: documentId }),
  }
);

const { id: sessionId } = await sessionRes.json();

// 2. Send message
const messageRes = await fetch(
  "https://noteai-kbsb.onrender.com/chat/message",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      content: "What is this document about?",
    }),
  }
);

const aiResponse = await messageRes.json();
// Response: { id, session_id, content: "AI answer...", role: "assistant", ... }
```

---

### Use Case 3: Create & Review Note

```javascript
// 1. Create note
const noteRes = await fetch("https://noteai-kbsb.onrender.com/notes/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Machine Learning Notes",
    content: "# Supervised Learning\n\n...",
    document_id: documentId,
  }),
});

const note = await noteRes.json();

// 2. Get AI review (detects language automatically)
const reviewRes = await fetch("https://noteai-kbsb.onrender.com/ai/review", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ note_id: note.id }),
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
const recsRes = await fetch(
  `https://noteai-kbsb.onrender.com/ai/recommendations/${documentId}`,
  {
    headers: { Authorization: `Bearer ${token}` },
  }
);

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
NEXT_PUBLIC_API_URL=https://noteai-kbsb.onrender.com

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

If you get CORS errors, contact backend team to add your domain.

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
                         │  Embeddings      │
                         └──────────────────┘
```

---

## 💡 Tips for Frontend Developers

### Token Management

```javascript
// Store token after login
localStorage.setItem("token", response.access_token);

// Use in requests
const token = localStorage.getItem("token");
fetch(url, {
  headers: { Authorization: `Bearer ${token}` },
});

// Handle 401 (expired token)
if (response.status === 401) {
  localStorage.removeItem("token");
  router.push("/login");
}
```

### Error Handling

```javascript
try {
  const res = await fetch(url, options);
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Request failed");
  }
  return await res.json();
} catch (error) {
  console.error("API Error:", error.message);
  // Show toast notification
}
```

### File Upload with Progress

```javascript
const formData = new FormData();
formData.append("file", file);

const xhr = new XMLHttpRequest();
xhr.upload.onprogress = (e) => {
  const percent = (e.loaded / e.total) * 100;
  setProgress(percent);
};

xhr.open("POST", `${API_URL}/files/upload/document`);
xhr.setRequestHeader("Authorization", `Bearer ${token}`);
xhr.send(formData);
```

### Language Detection (Automatic)

```javascript
// Just send your note content - AI detects language automatically
const note = {
  title: "Học máy",
  content: "# Supervised Learning\n\nHọc có giám sát là...",
};

// AI will respond in Vietnamese because content is Vietnamese
const review = await fetch(`${API_URL}/ai/review`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ note_id: noteId }),
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

## ⚡ Performance Notes

- **Document Processing**: Instant (0.0s for PDF/DOCX)
- **AI Review**: 2-5 seconds
- **Chat Response**: 1-3 seconds
- **Recommendations**: 2-4 seconds

All endpoints are async and optimized for production use.
