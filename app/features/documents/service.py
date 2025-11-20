"""
Document service - Business logic for document management
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Document, DocumentType, DocumentStatus
from app.schemas import DocumentCreate


class DocumentService:
    """Service class for document operations"""
    
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
    
    async def create_document(
        self,
        doc_type: DocumentType,
        source_url: str | None = None,
        content_hash: str | None = None
    ) -> Document:
        """
        Create a new document record
        
        Args:
            doc_type: Document type
            source_url: Optional source URL
            content_hash: Optional content hash
            
        Returns:
            Created document model
        """
        document = Document(
            user_id=self.current_user.id,
            type=doc_type,
            source_url=source_url,
            content_hash=content_hash,
            status=DocumentStatus.PROCESSING
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def list_documents(self) -> list[Document]:
        """
        List all documents for current user
        
        Returns:
            List of document models
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == self.current_user.id)
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_document(self, document_id: UUID) -> Document:
        """
        Get a specific document
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document model
            
        Raises:
            HTTPException: If document not found
        """
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == self.current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
    
    async def update_document_status(
        self,
        document_id: UUID,
        new_status: DocumentStatus
    ) -> Document:
        """
        Update document processing status
        
        Args:
            document_id: Document UUID
            new_status: New status
            
        Returns:
            Updated document model
        """
        document = await self.get_document(document_id)
        document.status = new_status
        
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def delete_document(self, document_id: UUID) -> None:
        """
        Delete a document
        
        Args:
            document_id: Document UUID
            
        Raises:
            HTTPException: If document not found
        """
        document = await self.get_document(document_id)
        
        await self.db.delete(document)
        await self.db.commit()
