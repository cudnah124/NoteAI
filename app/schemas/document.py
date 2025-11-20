"""
Document-related Pydantic schemas
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from app.models import DocumentType, DocumentStatus


class DocumentCreate(BaseModel):
    """Schema for creating document from URL"""
    type: DocumentType
    source_url: HttpUrl | None = None


class DocumentUpload(BaseModel):
    """Schema for document file upload (metadata)"""
    type: DocumentType = DocumentType.PDF


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: UUID
    user_id: UUID
    type: DocumentType
    source_url: str | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    """Schema for document status check"""
    id: UUID
    status: DocumentStatus
    message: str | None = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list"""
    documents: list[DocumentResponse]
    total: int


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk (internal use)"""
    id: UUID
    document_id: UUID
    content: str
    vector_id: str | None
    chunk_metadata: dict | None
    
    class Config:
        from_attributes = True
