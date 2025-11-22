# NoteAI API Documentation

**Base URL**: `http://localhost:8000`

## Authentication

Hầu hết endpoints yêu cầu JWT token:

```http
Authorization: Bearer <jwt_token>
```

Token có thời hạn 30 phút.

---

## Endpoints

### 1. Authentication (`/auth`)

#### POST `/auth/register`

Đăng ký tài khoản mới

**Request:**

```json
{
  "email": "user@example.com",
  "password": "Pass123!",
  "full_name": "John Doe" // optional
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-11-20T00:00:00"
}
```

#### POST `/auth/login`

Đăng nhập

**Request:**

```json
{
  "email": "user@example.com",
  "password": "Pass123!"
}
```

**Response (200):**

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### 2. Documents (`/documents`)

#### POST `/documents/upload`

Upload file (PDF, image)

**Request:** `multipart/form-data`

- `file`: File to upload

**Response (201):**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "pdf",
  "status": "processing",
  "created_at": "2025-11-20T00:00:00"
}
```

#### POST `/documents/url`

Xử lý tài liệu từ URL (web, YouTube)

**Request:**

```json
{
  "type": "web", // "pdf" | "web" | "youtube" | "image"
  "source_url": "https://example.com/page"
}
```

**Response (201):** Giống `/documents/upload`

#### GET `/documents/`

Lấy danh sách tài liệu của user

**Response (200):**

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "type": "pdf",
    "source_url": "https://...",
    "status": "processing",
    "created_at": "2025-11-20T00:00:00"
  }
]
```

#### GET `/documents/{document_id}`

Lấy thông tin 1 tài liệu

#### GET `/documents/{document_id}/status`

Kiểm tra trạng thái xử lý

**Response (200):**

```json
{
  "id": "uuid",
  "status": "processing", // "pending" | "processing" | "completed" | "failed"
  "message": "Document is processing"
}
```

#### DELETE `/documents/{document_id}`

Xóa tài liệu (204 No Content)

---

### 3. Chat (`/chat`)

#### POST `/chat/session`

Tạo chat session mới

**Request:**

```json
{
  "document_id": "uuid"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "document_id": "uuid",
  "created_at": "2025-11-20T00:00:00"
}
```

#### POST `/chat/message`

Gửi tin nhắn (RAG)

**Request:**

```json
{
  "session_id": "uuid",
  "content": "What is this document about?"
}
```

**Response (200):**

```json
{
  "id": "uuid",
  "session_id": "uuid",
  "content": "AI response...",
  "role": "assistant",
  "created_at": "2025-11-20T00:00:00"
}
```

#### GET `/chat/session/{session_id}/messages`

Lấy lịch sử chat

**Response (200):**

```json
[
  {
    "id": "uuid",
    "session_id": "uuid",
    "content": "Hello",
    "role": "user",
    "created_at": "2025-11-20T00:00:00"
  }
]
```

#### GET `/chat/sessions?document_id={uuid}`

Lấy danh sách sessions (filter optional)

#### DELETE `/chat/session/{session_id}`

Xóa session (204 No Content)

---

### 4. Notes (`/notes`)

#### POST `/notes/`

Tạo ghi chú mới

**Request:**

```json
{
  "title": "My Notes",
  "content": "# Content in markdown",
  "document_id": "uuid" // optional
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "document_id": "uuid",
  "title": "My Notes",
  "content": "# Content",
  "created_at": "2025-11-20T00:00:00",
  "updated_at": "2025-11-20T00:00:00"
}
```

#### GET `/notes/`

Lấy danh sách ghi chú

**Response (200):** Array of notes

#### GET `/notes/{note_id}`

Lấy 1 ghi chú

#### PUT `/notes/{note_id}`

Cập nhật ghi chú

**Request:**

```json
{
  "title": "Updated Title",
  "content": "Updated content"
}
```

#### DELETE `/notes/{note_id}`

Xóa ghi chú (204 No Content)

---

### 5. AI Services (`/ai`)

#### POST `/ai/review`

AI review ghi chú

**Request:**

```json
{
  "note_id": "uuid"
}
```

**Response (200):**

```json
{
  "note_id": "uuid",
  "correctness_score": 8,
  "misunderstandings": ["Point 1", "Point 2"],
  "missing_points": ["Add more examples"],
  "constructive_feedback": "Overall good..."
}
```

#### GET `/ai/recommend/{document_id}`

Lấy đề xuất học tập

**Response (200):**

```json
{
  "document_id": "uuid",
  "recommendations": ["Study topic A", "Review concept B"]
}
```

---

## Error Responses

```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**

- `200` - Success
- `201` - Created
- `204` - No Content (delete success)
- `400` - Bad Request
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

---

## Complete Workflow Example

```python
import httpx

BASE_URL = "http://localhost:8000"

async def complete_workflow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Register & Login
        await client.post("/auth/register", json={
            "email": "user@test.com",
            "password": "Pass123!"
        })

        login = await client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "Pass123!"
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload Document
        doc = await client.post("/documents/url",
            json={"type": "web", "source_url": "https://example.com"},
            headers=headers
        )
        doc_id = doc.json()["id"]

        # 3. Create Note
        note = await client.post("/notes/",
            json={"title": "Study Notes", "content": "# Content", "document_id": doc_id},
            headers=headers
        )
        note_id = note.json()["id"]

        # 4. Chat with AI
        session = await client.post("/chat/session",
            json={"document_id": doc_id},
            headers=headers
        )
        session_id = session.json()["id"]

        message = await client.post("/chat/message",
            json={"session_id": session_id, "content": "What is this about?"},
            headers=headers
        )

        # 5. AI Review
        review = await client.post("/ai/review",
            json={"note_id": note_id},
            headers=headers
        )
```

**Reference:** See `test_api.py` for complete integration test examples.

**Request Body**:

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

**Response** (200 OK):

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "created_at": "2025-11-20T10:00:00Z"
}
```

**Errors**:

- `400`: Email hoặc username đã tồn tại
- `422`: Validation error (email không hợp lệ, password quá ngắn, etc.)

---

### POST `/auth/login`

Đăng nhập và nhận JWT token

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe"
  }
}
```

**Errors**:

- `401`: Email hoặc password không đúng

---

## Notes Endpoints

**Yêu cầu**: Bearer token

### POST `/notes`

Tạo ghi chú mới

**Request Body**:

```json
{
  "title": "Chương 1: Introduction to AI",
  "content": "# Introduction\n\nAI is the simulation of human intelligence...",
  "document_id": "uuid-of-document",
  "tags": ["ai", "machine-learning"]
}
```

**Response** (201 Created):

```json
{
  "id": "uuid",
  "title": "Chương 1: Introduction to AI",
  "content": "# Introduction\n\nAI is...",
  "document_id": "uuid-of-document",
  "user_id": "uuid",
  "tags": ["ai", "machine-learning"],
  "created_at": "2025-11-20T10:00:00Z",
  "updated_at": "2025-11-20T10:00:00Z"
}
```

---

### GET `/notes`

Lấy danh sách ghi chú của user

**Query Parameters**:

- `skip` (int, optional): Số bản ghi bỏ qua (default: 0)
- `limit` (int, optional): Số bản ghi trả về (default: 100, max: 100)

**Response** (200 OK):

```json
[
  {
    "id": "uuid",
    "title": "Chương 1: Introduction to AI",
    "content": "...",
    "document_id": "uuid",
    "tags": ["ai"],
    "created_at": "2025-11-20T10:00:00Z",
    "updated_at": "2025-11-20T10:00:00Z"
  }
]
```

---

### GET `/notes/{note_id}`

Lấy chi tiết một ghi chú

**Path Parameters**:

- `note_id` (uuid): ID của ghi chú

**Response** (200 OK):

```json
{
  "id": "uuid",
  "title": "Chương 1: Introduction to AI",
  "content": "Full content here...",
  "document_id": "uuid",
  "tags": ["ai", "machine-learning"],
  "created_at": "2025-11-20T10:00:00Z",
  "updated_at": "2025-11-20T10:00:00Z"
}
```

**Errors**:

- `404`: Note không tồn tại hoặc không thuộc user

---

### PUT `/notes/{note_id}`

Cập nhật ghi chú

**Path Parameters**:

- `note_id` (uuid): ID của ghi chú

**Request Body**:

```json
{
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["new-tag"]
}
```

**Response** (200 OK):

```json
{
  "id": "uuid",
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["new-tag"],
  "updated_at": "2025-11-20T11:00:00Z"
}
```

**Errors**:

- `404`: Note không tồn tại

---

### DELETE `/notes/{note_id}`

Xóa ghi chú

**Path Parameters**:

- `note_id` (uuid): ID của ghi chú

**Response** (204 No Content)

**Errors**:

- `404`: Note không tồn tại

---

## Documents Endpoints

**Yêu cầu**: Bearer token

### POST `/documents/upload`

Upload file PDF hoặc ảnh

**Content-Type**: `multipart/form-data`

**Form Data**:

- `file`: File PDF hoặc ảnh (max 10MB)
- `title` (optional): Tiêu đề tài liệu

**Response** (201 Created):

```json
{
  "id": "uuid",
  "title": "Machine Learning Textbook",
  "source_type": "upload",
  "file_path": "/uploads/uuid.pdf",
  "processing_status": "pending",
  "user_id": "uuid",
  "created_at": "2025-11-20T10:00:00Z"
}
```

**Processing Status**:

- `pending`: Đang chờ xử lý
- `processing`: Đang xử lý
- `completed`: Hoàn thành
- `failed`: Thất bại

---

### POST `/files/upload/document`

**Frontend-compatible upload endpoint** - Wraps `/documents/upload` with frontend-expected response format

**Content-Type**: `multipart/form-data`

**Form Data**:

- `file`: File PDF, DOCX hoặc ảnh (max 10MB)

**Response** (200 OK):

```json
{
  "success": true,
  "document": {
    "id": "uuid",
    "etag": "uuid",
    "type": "pdf",
    "status": "processing",
    "title": "Machine Learning Textbook",
    "created_at": "2025-11-20T10:00:00Z"
  }
}
```

**Supported File Types**:

- PDF: `.pdf`
- Word Documents: `.docx`
- Images: `.png`, `.jpg`, `.jpeg`

**Note**: This endpoint is designed for frontend compatibility. It returns `etag` field (same as document ID) and simplified status fields. Processing is instant for both PDF and DOCX files (typically 0.0s).

---

### POST `/documents/url`

Xử lý tài liệu từ URL (YouTube, web)

**Request Body**:

```json
{
  "url": "https://www.youtube.com/watch?v=xyz",
  "title": "AI Lecture Video"
}
```

**Response** (201 Created):

```json
{
  "id": "uuid",
  "title": "AI Lecture Video",
  "source_type": "url",
  "source_url": "https://www.youtube.com/watch?v=xyz",
  "processing_status": "pending",
  "created_at": "2025-11-20T10:00:00Z"
}
```

---

### GET `/documents/{document_id}/status`

Kiểm tra trạng thái xử lý tài liệu

**Path Parameters**:

- `document_id` (uuid): ID của tài liệu

**Response** (200 OK):

```json
{
  "id": "uuid",
  "processing_status": "completed",
  "progress_percentage": 100,
  "total_chunks": 45,
  "error_message": null
}
```

**Status Values**:

- `pending`: Chưa bắt đầu (0%)
- `processing`: Đang xử lý (1-99%)
- `completed`: Hoàn thành (100%)
- `failed`: Lỗi

---

### GET `/documents`

Lấy danh sách tài liệu

**Query Parameters**:

- `skip` (int): Offset (default: 0)
- `limit` (int): Limit (default: 100)

**Response** (200 OK):

```json
[
  {
    "id": "uuid",
    "title": "Machine Learning Textbook",
    "source_type": "upload",
    "processing_status": "completed",
    "total_chunks": 45,
    "created_at": "2025-11-20T10:00:00Z"
  }
]
```

---

### GET `/documents/{document_id}`

Lấy chi tiết tài liệu

**Path Parameters**:

- `document_id` (uuid): ID của tài liệu

**Response** (200 OK):

```json
{
  "id": "uuid",
  "title": "Machine Learning Textbook",
  "source_type": "upload",
  "file_path": "/uploads/uuid.pdf",
  "processing_status": "completed",
  "total_chunks": 45,
  "file_hash": "sha256hash",
  "metadata": {
    "pages": 350,
    "file_size": 5242880
  },
  "created_at": "2025-11-20T10:00:00Z"
}
```

---

### DELETE `/documents/{document_id}`

Xóa tài liệu và tất cả chunks

**Path Parameters**:

- `document_id` (uuid): ID của tài liệu

**Response** (204 No Content)

**Errors**:

- `404`: Document không tồn tại

---

## Chat Endpoints

**Yêu cầu**: Bearer token

### POST `/chat/session`

Tạo phiên chat mới

**Request Body**:

```json
{
  "document_id": "uuid",
  "title": "Q&A about Machine Learning"
}
```

**Response** (201 Created):

```json
{
  "id": "uuid",
  "title": "Q&A about Machine Learning",
  "document_id": "uuid",
  "user_id": "uuid",
  "created_at": "2025-11-20T10:00:00Z"
}
```

---

### POST `/chat/message`

Gửi câu hỏi trong phiên chat

**Request Body**:

```json
{
  "session_id": "uuid",
  "content": "What is supervised learning?"
}
```

**Response** (200 OK):

```json
{
  "id": "uuid",
  "session_id": "uuid",
  "role": "assistant",
  "content": "Supervised learning is a type of machine learning where the model is trained on labeled data. The algorithm learns from input-output pairs...",
  "metadata": {
    "retrieved_chunks": 5,
    "confidence": 0.92
  },
  "created_at": "2025-11-20T10:05:00Z"
}
```

**Note**: Hệ thống tự động lưu cả câu hỏi của user và câu trả lời của AI.

---

### GET `/chat/session/{session_id}/messages`

Lấy lịch sử chat

**Path Parameters**:

- `session_id` (uuid): ID của phiên chat

**Query Parameters**:

- `skip` (int): Offset (default: 0)
- `limit` (int): Limit (default: 50)

**Response** (200 OK):

```json
[
  {
    "id": "uuid",
    "role": "user",
    "content": "What is supervised learning?",
    "created_at": "2025-11-20T10:05:00Z"
  },
  {
    "id": "uuid",
    "role": "assistant",
    "content": "Supervised learning is...",
    "created_at": "2025-11-20T10:05:05Z"
  }
]
```

---

### GET `/chat/sessions`

Lấy danh sách phiên chat

**Query Parameters**:

- `skip` (int): Offset (default: 0)
- `limit` (int): Limit (default: 100)

**Response** (200 OK):

```json
[
  {
    "id": "uuid",
    "title": "Q&A about Machine Learning",
    "document_id": "uuid",
    "message_count": 12,
    "created_at": "2025-11-20T10:00:00Z",
    "updated_at": "2025-11-20T10:30:00Z"
  }
]
```

---

### DELETE `/chat/session/{session_id}`

Xóa phiên chat và tất cả messages

**Path Parameters**:

- `session_id` (uuid): ID của phiên chat

**Response** (204 No Content)

---

## AI Services Endpoints

**Yêu cầu**: Bearer token

### POST `/ai/review`

**AI-powered note review với language detection tự động**

Phân tích và đánh giá ghi chú của user, tự động phát hiện ngôn ngữ của ghi chú và trả về review bằng chính ngôn ngữ đó.

**Language Detection**:

- Hệ thống tự động detect ngôn ngữ từ nội dung ghi chú (Vietnamese/English)
- Response sẽ được trả về hoàn toàn bằng ngôn ngữ được detect
- Không cần client chỉ định ngôn ngữ

**Request Body**:

```json
{
  "note_id": "uuid"
}
```

**Response (200 OK)** - Ví dụ với ghi chú tiếng Việt:

```json
{
  "note_id": "uuid",
  "overall_feedback": "Ghi chú của bạn cho thấy sự hiểu biết tốt về các khái niệm cơ bản của machine learning...",
  "strengths": [
    "Giải thích rõ ràng về supervised learning với các ví dụ cụ thể",
    "Phân biệt tốt giữa classification và regression",
    "Cấu trúc ghi chú logic và dễ theo dõi"
  ],
  "areas_for_improvement": [
    "Nên bổ sung thêm về unsupervised learning để có cái nhìn toàn diện",
    "Thiếu các ví dụ về thuật toán cụ thể như decision trees, SVM",
    "Chưa đề cập đến các vấn đề về overfitting và underfitting"
  ],
  "specific_corrections": [
    "Neural networks không phải là phương pháp duy nhất trong deep learning - còn có CNN, RNN, Transformers",
    "Supervised learning không chỉ áp dụng cho classification mà còn cho regression"
  ],
  "suggestions_for_expansion": [
    "Thêm phần về cross-validation và model evaluation metrics",
    "Bổ sung ví dụ thực tế về các bộ dataset nổi tiếng (MNIST, ImageNet)",
    "Giải thích về feature engineering và data preprocessing"
  ]
}
```

**Response (200 OK)** - Ví dụ với ghi chú tiếng Anh:

```json
{
  "note_id": "uuid",
  "overall_feedback": "Your notes demonstrate a solid understanding of fundamental machine learning concepts...",
  "strengths": [
    "Clear explanation of supervised learning with concrete examples",
    "Good distinction between classification and regression",
    "Logical structure that's easy to follow"
  ],
  "areas_for_improvement": [
    "Should add more about unsupervised learning for completeness",
    "Missing examples of specific algorithms like decision trees, SVM",
    "No mention of overfitting and underfitting issues"
  ],
  "specific_corrections": [
    "Neural networks aren't the only method in deep learning - there are CNNs, RNNs, Transformers",
    "Supervised learning applies to both classification and regression"
  ],
  "suggestions_for_expansion": [
    "Add section on cross-validation and model evaluation metrics",
    "Include real-world examples of famous datasets (MNIST, ImageNet)",
    "Explain feature engineering and data preprocessing"
  ]
}
```

**Fields Explanation**:

- `overall_feedback` (string): Tổng quan về chất lượng ghi chú
- `strengths` (array): 2-3 điểm mạnh của ghi chú
- `areas_for_improvement` (array): 2-3 điểm cần cải thiện
- `specific_corrections` (array): Các điểm hiểu sai cần sửa (có thể rỗng nếu không có lỗi)
- `suggestions_for_expansion` (array): Gợi ý mở rộng kiến thức

**Technical Details**:

- Uses HyperCLOVA X with temperature=0.7, max_tokens=2000
- Language detection based on Unicode characters in first 200 chars
- Response parsing supports both Vietnamese and English section markers
- Typically responds in 2-5 seconds

**Errors**:

- `404`: Note không tồn tại hoặc không thuộc user
- `500`: LLM service error

---

### GET `/ai/recommendations/{document_id}`

**Đề xuất học tập thông minh với language detection**

Phân tích tài liệu và ghi chú để đề xuất các chủ đề nên học thêm, tự động detect ngôn ngữ từ ghi chú của user.

**Path Parameters**:

- `document_id` (uuid): ID của tài liệu

**Language Detection**:

- Hệ thống analyze ngôn ngữ từ tất cả ghi chú liên quan đến document
- Recommendations được trả về bằng ngôn ngữ chiếm đa số trong các ghi chú

**Response (200 OK)** - Ví dụ tiếng Việt:

```json
{
  "document_id": "uuid",
  "missing_sections": [
    "Chương 5: Neural Networks và Deep Learning",
    "Chương 8: Reinforcement Learning",
    "Phần 3.2: Gradient Descent và Optimization"
  ],
  "key_concepts_to_review": [
    "Backpropagation algorithm - thuật toán học của neural networks",
    "Convolutional Neural Networks (CNN) cho computer vision",
    "Recurrent Neural Networks (RNN) cho xử lý chuỗi",
    "Transfer learning và pretrained models"
  ],
  "coverage_percentage": 65,
  "overall_recommendation": "Bạn đã hoàn thành 65% nội dung tài liệu, cho thấy sự tiến bộ tốt. Tập trung vào các chủ đề về neural networks và deep learning sẽ giúp bạn có cái nhìn toàn diện hơn về machine learning hiện đại. Đặc biệt chú ý đến backpropagation - đây là thuật toán cốt lõi giúp neural networks học được. Sau khi nắm vững phần này, hãy chuyển sang reinforcement learning để hiểu về học tăng cường."
}
```

**Response (200 OK)** - Ví dụ tiếng Anh:

```json
{
  "document_id": "uuid",
  "missing_sections": [
    "Chapter 5: Neural Networks and Deep Learning",
    "Chapter 8: Reinforcement Learning",
    "Section 3.2: Gradient Descent and Optimization"
  ],
  "key_concepts_to_review": [
    "Backpropagation algorithm - the learning mechanism of neural networks",
    "Convolutional Neural Networks (CNN) for computer vision",
    "Recurrent Neural Networks (RNN) for sequence processing",
    "Transfer learning and pretrained models"
  ],
  "coverage_percentage": 65,
  "overall_recommendation": "You've completed 65% of the document content, showing good progress. Focusing on neural networks and deep learning topics will give you a more comprehensive view of modern machine learning. Pay special attention to backpropagation - this is the core algorithm that enables neural networks to learn. Once you master this, move on to reinforcement learning to understand how agents learn from interaction."
}
```

**Fields Explanation**:

- `missing_sections` (array): Các phần trong document chưa được ghi chú
- `key_concepts_to_review` (array): Các concept quan trọng nên tập trung học
- `coverage_percentage` (int): % tài liệu đã được cover (0-100)
- `overall_recommendation` (string): Lời khuyên chi tiết về lộ trình học tiếp

**Technical Details**:

- Uses HyperCLOVA X with temperature=0.7, max_tokens=1500
- Analyzes all notes related to the document
- Language detection from combined note content (first 500 chars)
- Coverage calculated based on note count vs document chunks

**Errors**:

- `404`: Document không tồn tại hoặc không thuộc user
- `500`: LLM service error

---

### GET `/ai/recommend/{document_id}`

**Deprecated**: Use `/ai/recommendations/{document_id}` instead

Đề xuất chủ đề cần học thêm (old format - maintained for backward compatibility)

**Path Parameters**:

- `document_id` (uuid): ID của tài liệu

**Response (200 OK)**:

```json
{
  "document_id": "uuid",
  "missing_sections": [
    "Chapter 5: Neural Networks",
    "Chapter 8: Reinforcement Learning"
  ],
  "suggested_topics": [
    "Backpropagation algorithm",
    "Convolutional Neural Networks",
    "Q-learning và policy gradient"
  ],
  "coverage_percentage": 65,
  "recommendations": "Bạn đã hoàn thành 65% nội dung tài liệu..."
}
```

---

## Data Models

### User

```typescript
interface User {
  id: string; // UUID
  email: string; // Email unique
  username: string; // Username unique
  full_name?: string; // Optional full name
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}
```

### Document

```typescript
interface Document {
  id: string;
  title: string;
  source_type: "upload" | "url";
  file_path?: string;
  source_url?: string;
  processing_status: "pending" | "processing" | "completed" | "failed";
  file_hash?: string;
  metadata?: Record<string, any>;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

### Note

```typescript
interface Note {
  id: string;
  title: string;
  content: string; // Markdown format
  document_id: string;
  user_id: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}
```

### ChatSession

```typescript
interface ChatSession {
  id: string;
  title: string;
  document_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

### ChatMessage

```typescript
interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning          | Description              |
| ---- | ---------------- | ------------------------ |
| 200  | OK               | Request successful       |
| 201  | Created          | Resource created         |
| 204  | No Content       | Deleted successfully     |
| 400  | Bad Request      | Invalid request data     |
| 401  | Unauthorized     | Missing or invalid token |
| 403  | Forbidden        | No permission            |
| 404  | Not Found        | Resource not found       |
| 422  | Validation Error | Invalid input data       |
| 500  | Server Error     | Internal server error    |

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Frontend Integration

### Setup Axios Instance

```typescript
// api/client.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

### Authentication Service

```typescript
// services/authService.ts
import api from "../api/client";

export const authService = {
  async register(data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  async login(email: string, password: string) {
    const response = await api.post("/auth/login", { email, password });
    const { access_token, user } = response.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("user", JSON.stringify(user));
    return response.data;
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  },

  getCurrentUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },
};
```

---

### Documents Service

```typescript
// services/documentsService.ts
import api from "../api/client";

export const documentsService = {
  async upload(file: File, title?: string) {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);

    const response = await api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async uploadFromUrl(url: string, title: string) {
    const response = await api.post("/documents/url", { url, title });
    return response.data;
  },

  async getStatus(documentId: string) {
    const response = await api.get(`/documents/${documentId}/status`);
    return response.data;
  },

  async list(skip = 0, limit = 100) {
    const response = await api.get("/documents", { params: { skip, limit } });
    return response.data;
  },

  async get(documentId: string) {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  async delete(documentId: string) {
    await api.delete(`/documents/${documentId}`);
  },
};
```

---

### Notes Service

```typescript
// services/notesService.ts
import api from "../api/client";

export const notesService = {
  async create(data: {
    title: string;
    content: string;
    document_id: string;
    tags?: string[];
  }) {
    const response = await api.post("/notes", data);
    return response.data;
  },

  async list(skip = 0, limit = 100) {
    const response = await api.get("/notes", { params: { skip, limit } });
    return response.data;
  },

  async get(noteId: string) {
    const response = await api.get(`/notes/${noteId}`);
    return response.data;
  },

  async update(
    noteId: string,
    data: {
      title?: string;
      content?: string;
      tags?: string[];
    }
  ) {
    const response = await api.put(`/notes/${noteId}`, data);
    return response.data;
  },

  async delete(noteId: string) {
    await api.delete(`/notes/${noteId}`);
  },
};
```

---

### Chat Service

```typescript
// services/chatService.ts
import api from "../api/client";

export const chatService = {
  async createSession(documentId: string, title: string) {
    const response = await api.post("/chat/session", {
      document_id: documentId,
      title,
    });
    return response.data;
  },

  async sendMessage(sessionId: string, content: string) {
    const response = await api.post("/chat/message", {
      session_id: sessionId,
      content,
    });
    return response.data;
  },

  async getMessages(sessionId: string, skip = 0, limit = 50) {
    const response = await api.get(`/chat/session/${sessionId}/messages`, {
      params: { skip, limit },
    });
    return response.data;
  },

  async listSessions(skip = 0, limit = 100) {
    const response = await api.get("/chat/sessions", {
      params: { skip, limit },
    });
    return response.data;
  },

  async deleteSession(sessionId: string) {
    await api.delete(`/chat/session/${sessionId}`);
  },
};
```

---

### AI Service

```typescript
// services/aiService.ts
import api from "../api/client";

export const aiService = {
  async reviewNote(noteId: string) {
    const response = await api.post("/ai/review", { note_id: noteId });
    return response.data;
  },

  async getRecommendations(documentId: string) {
    const response = await api.get(`/ai/recommend/${documentId}`);
    return response.data;
  },
};
```

---

## Examples

### Complete Workflow Example

#### 1. Đăng ký tài khoản

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student123",
    "password": "SecurePass123",
    "full_name": "Nguyen Van A"
  }'
```

#### 2. Đăng nhập

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 3. Upload tài liệu

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer eyJhbGc..." \
  -F "file=@textbook.pdf" \
  -F "title=Machine Learning Textbook"
```

#### 4. Kiểm tra trạng thái xử lý

```bash
curl -X GET http://localhost:8000/documents/{document_id}/status \
  -H "Authorization: Bearer eyJhbGc..."
```

#### 5. Tạo ghi chú

```bash
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chapter 1 Notes",
    "content": "# Supervised Learning\n\n...",
    "document_id": "{document_id}",
    "tags": ["ml", "supervised-learning"]
  }'
```

#### 6. Tạo phiên chat

```bash
curl -X POST http://localhost:8000/chat/session \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "{document_id}",
    "title": "Q&A Session"
  }'
```

#### 7. Hỏi câu hỏi

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "{session_id}",
    "content": "What is the difference between supervised and unsupervised learning?"
  }'
```

#### 8. Review ghi chú

```bash
curl -X POST http://localhost:8000/ai/review \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "note_id": "{note_id}"
  }'
```

#### 9. Nhận đề xuất học tập

```bash
curl -X GET http://localhost:8000/ai/recommend/{document_id} \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## React Component Examples

### Login Component

```typescript
import { useState } from "react";
import { authService } from "./services/authService";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authService.login(email, password);
      window.location.href = "/dashboard";
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Document Upload Component

```typescript
import { useState } from "react";
import { documentsService } from "./services/documentsService";

function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      const doc = await documentsService.upload(file, title);
      console.log("Document uploaded:", doc);
      // Poll for status
      checkStatus(doc.id);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const checkStatus = async (documentId: string) => {
    const status = await documentsService.getStatus(documentId);
    console.log("Status:", status);
    if (status.processing_status !== "completed") {
      setTimeout(() => checkStatus(documentId), 2000);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".pdf,image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Document title"
      />
      <button type="submit">Upload</button>
    </form>
  );
}
```

### Chat Component

```typescript
import { useState, useEffect } from "react";
import { chatService } from "./services/chatService";

function ChatInterface({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    loadMessages();
  }, [sessionId]);

  const loadMessages = async () => {
    const msgs = await chatService.getMessages(sessionId);
    setMessages(msgs);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to UI
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");

    // Send to API
    const response = await chatService.sendMessage(sessionId, input);

    // Add AI response to UI
    setMessages((prev) => [...prev, response]);
  };

  return (
    <div>
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
```

---

## Rate Limiting

- **Auth endpoints**: 5 requests/minute/IP
- **Upload endpoints**: 10 requests/hour/user
- **Chat endpoints**: 30 requests/minute/user
- **Other endpoints**: 100 requests/minute/user

---

## CORS Configuration

Allowed origins:

- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- Production domain (TBD)

---

**Last Updated**: November 20, 2025  
**API Version**: 1.0.0  
**Documentation**: For Frontend Developers
