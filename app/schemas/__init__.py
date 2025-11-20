"""
Pydantic Schemas Layer
Organized by entity for API request/response validation
"""
from .user import UserCreate, UserLogin, UserResponse, Token, TokenData
from .document import (
    DocumentCreate,
    DocumentUpload,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentListResponse,
    DocumentChunkResponse,
)
from .note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from .chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatSessionListResponse,
)
from .ai import ReviewRequest, ReviewResponse, RecommendationResponse

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    # Document
    "DocumentCreate",
    "DocumentUpload",
    "DocumentResponse",
    "DocumentStatusResponse",
    "DocumentListResponse",
    "DocumentChunkResponse",
    # Note
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "NoteListResponse",
    # Chat
    "ChatSessionCreate",
    "ChatSessionResponse",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ChatSessionListResponse",
    # AI
    "ReviewRequest",
    "ReviewResponse",
    "RecommendationResponse",
]
