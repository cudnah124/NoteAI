"""
Note-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class NoteCreate(BaseModel):
    """Schema for creating a note"""
    document_id: UUID
    title: str | None = Field(None, max_length=500, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")


class NoteUpdate(BaseModel):
    """Schema for updating a note"""
    title: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)


class NoteResponse(BaseModel):
    """Schema for note response"""
    id: UUID
    user_id: UUID
    document_id: UUID
    title: str | None
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for note list"""
    notes: list[NoteResponse]
    total: int
