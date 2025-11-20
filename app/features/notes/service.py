"""
Notes service - Business logic for note management
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Note, Document
from app.schemas import NoteCreate, NoteUpdate


class NoteService:
    """Service class for note operations"""
    
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
    
    async def create_note(self, note_data: NoteCreate) -> Note:
        """
        Create a new note
        
        Args:
            note_data: Note creation data
            
        Returns:
            Created note model
            
        Raises:
            HTTPException: If document not found or doesn't belong to user
        """
        # Verify document exists and belongs to user
        result = await self.db.execute(
            select(Document).where(
                Document.id == note_data.document_id,
                Document.user_id == self.current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        # Create note
        note = Note(
            user_id=self.current_user.id,
            document_id=note_data.document_id,
            title=note_data.title,
            content=note_data.content
        )
        
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        
        return note
    
    async def list_notes(self, document_id: UUID | None = None) -> list[Note]:
        """
        List user's notes, optionally filtered by document
        
        Args:
            document_id: Optional document ID to filter by
            
        Returns:
            List of note models
        """
        query = select(Note).where(Note.user_id == self.current_user.id)
        
        if document_id:
            query = query.where(Note.document_id == document_id)
        
        query = query.order_by(Note.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_note(self, note_id: UUID) -> Note:
        """
        Get a specific note
        
        Args:
            note_id: Note UUID
            
        Returns:
            Note model
            
        Raises:
            HTTPException: If note not found
        """
        result = await self.db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == self.current_user.id
            )
        )
        note = result.scalar_one_or_none()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        return note
    
    async def update_note(self, note_id: UUID, note_data: NoteUpdate) -> Note:
        """
        Update a note
        
        Args:
            note_id: Note UUID
            note_data: Updated note data
            
        Returns:
            Updated note model
            
        Raises:
            HTTPException: If note not found
        """
        note = await self.get_note(note_id)
        
        # Update fields
        if note_data.title is not None:
            note.title = note_data.title
        if note_data.content is not None:
            note.content = note_data.content
        
        await self.db.commit()
        await self.db.refresh(note)
        
        return note
    
    async def delete_note(self, note_id: UUID) -> None:
        """
        Delete a note
        
        Args:
            note_id: Note UUID
            
        Raises:
            HTTPException: If note not found
        """
        note = await self.get_note(note_id)
        
        await self.db.delete(note)
        await self.db.commit()
