"""
Document and DocumentChunk models
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    WORD = "word"
    YOUTUBE = "youtube"
    WEB = "web"
    IMAGE = "image"
    VIDEO = "video"


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """Document model for uploaded/processed documents"""
    __tablename__ = "documents"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(DocumentType), nullable=False)
    source_url = Column(Text, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PROCESSING, index=True)
    content_hash = Column(String(64), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="document", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.id} ({self.type.value})>"


class DocumentChunk(BaseModel):
    """Document chunk model for vector storage"""
    __tablename__ = "document_chunks"
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    vector_id = Column(String(255), nullable=True, index=True)
    chunk_metadata = Column(JSON, nullable=True)  # {page_num, start_time, end_time, chunk_index}
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk {self.id}>"
