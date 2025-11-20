"""
Document API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core import get_db, get_current_user
from app.models import User, DocumentType, DocumentStatus
from app.schemas import DocumentCreate, DocumentResponse, DocumentStatusResponse
from .service import DocumentService
from .processor import DocumentProcessor

router = APIRouter(prefix="/documents", tags=["Documents"])

# Document processor instance
processor = DocumentProcessor()


def get_document_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DocumentService:
    """Dependency to get document service instance"""
    return DocumentService(db, current_user)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document file",
    description="Upload PDF, image, or video file for processing"
)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service)
):
    """Upload a document file (PDF, image, video, etc.)"""
    # Determine document type from file extension
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        doc_type = DocumentType.PDF
    elif filename.endswith(('.jpg', '.jpeg', '.png')):
        doc_type = DocumentType.IMAGE
    elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        doc_type = DocumentType.VIDEO
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF, images, and videos are supported."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Calculate hash
    content_hash = processor.calculate_hash(file_content)
    
    # Create document record
    document = await service.create_document(
        doc_type=doc_type,
        content_hash=content_hash
    )
    
    # TODO: Trigger async processing task
    # from app.tasks import process_document_task
    # process_document_task.delay(str(document.id), file_content, doc_type.value)
    
    return document


@router.post(
    "/url",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process URL",
    description="Process document from URL (YouTube, web, etc.)"
)
async def process_url(
    doc_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Process a document from URL"""
    if not doc_data.source_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_url is required"
        )
    
    # Create document record
    document = await service.create_document(
        doc_type=doc_data.type,
        source_url=str(doc_data.source_url)
    )
    
    # For YouTube URLs, process immediately using fast transcript API
    if doc_data.type == DocumentType.YOUTUBE:
        try:
            text, chunks = await processor.process_youtube_url(str(doc_data.source_url))
            
            # Store chunks (simplified - in production use vector DB)
            from app.models import DocumentChunk
            for chunk_data in chunks[:10]:  # Limit for demo
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_data["content"],
                    chunk_metadata=chunk_data.get("metadata", {})
                )
                service.db.add(chunk)
            
            # Update status to completed
            document.status = DocumentStatus.COMPLETED
            await service.db.commit()
            await service.db.refresh(document)
            
        except Exception as e:
            document.status = DocumentStatus.FAILED
            await service.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"YouTube processing failed: {str(e)}"
            )
    
    # TODO: For other types, trigger async processing task
    # from app.tasks import process_document_task
    # process_document_task.delay(str(document.id), None, doc_data.type.value, str(doc_data.source_url))
    
    return document


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get document status",
    description="Check document processing status"
)
async def get_document_status(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get document processing status"""
    document = await service.get_document(document_id)
    
    return DocumentStatusResponse(
        id=document.id,
        status=document.status,
        message=f"Document is {document.status.value}"
    )


@router.get(
    "/",
    response_model=list[DocumentResponse],
    summary="List documents",
    description="Get all documents for current user"
)
async def list_documents(
    service: DocumentService = Depends(get_document_service)
):
    """List all user's documents"""
    return await service.list_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document",
    description="Get a specific document by ID"
)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get a specific document"""
    return await service.get_document(document_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and all its chunks"
)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    await service.delete_document(document_id)
