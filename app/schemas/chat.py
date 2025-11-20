"""
Chat-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.models import MessageRole


class ChatSessionCreate(BaseModel):
    """Schema for creating chat session"""
    document_id: UUID


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: UUID
    user_id: UUID
    document_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Schema for sending chat message"""
    session_id: UUID
    content: str = Field(..., min_length=1, description="Message content/question")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: UUID
    session_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history"""
    session_id: UUID
    messages: list[ChatMessageResponse]
    total: int


class ChatSessionListResponse(BaseModel):
    """Schema for chat session list"""
    sessions: list[ChatSessionResponse]
    total: int
