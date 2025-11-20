"""
Note model
"""
from sqlalchemy import Column, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class Note(BaseModel):
    """Note model for user study notes"""
    __tablename__ = "notes"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    context_vector_id = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    document = relationship("Document", back_populates="notes")
    
    def __repr__(self):
        return f"<Note {self.id} - {self.title or 'Untitled'}>"
