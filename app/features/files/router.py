"""
Files router - Adapter for frontend compatibility
Maps /files/* endpoints to existing /notes/* and /documents/* endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core import get_db, get_current_user
from app.models import User
from app.schemas import NoteResponse, DocumentResponse

router = APIRouter(prefix="/files", tags=["Files"])


@router.get(
    "/metadata/note",
    response_model=dict,
    summary="Get notes metadata",
    description="Get all notes metadata for current user (Frontend compatibility endpoint)"
)
async def get_notes_metadata(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notes metadata - frontend compatibility"""
    from app.features.notes.service import NoteService
    
    service = NoteService(db, current_user)
    notes = await service.list_notes()
    
    # Transform to frontend expected format
    files = []
    for note in notes:
        files.append({
            "file_name": note.title or f"Note-{note.id}",
            "size": len(note.content.encode('utf-8')) if note.content else 0,
            "last_modified": note.updated_at.isoformat(),
            "etag": str(note.id),  # Use UUID as etag
            "preview_url": f"/files/content/note/{note.id}"
        })
    
    return {"files": files}


@router.get(
    "/content/note/{etag}",
    response_model=str,
    summary="Get note raw content",
    description="Get raw markdown content of a note by etag (Frontend compatibility endpoint)"
)
async def get_note_content(
    etag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get raw note content - frontend compatibility"""
    from app.features.notes.service import NoteService
    
    try:
        note_id = UUID(etag)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid etag format"
        )
    
    service = NoteService(db, current_user)
    note = await service.get_note(note_id)
    
    # Return raw markdown content
    return PlainTextResponse(content=note.content or "")


@router.get(
    "/metadata/document",
    response_model=dict,
    summary="Get documents metadata",
    description="Get all documents metadata for current user (Frontend compatibility endpoint)"
)
async def get_documents_metadata(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents metadata - frontend compatibility"""
    from app.features.documents.service import DocumentService
    
    service = DocumentService(db, current_user)
    documents = await service.list_documents()
    
    # Transform to frontend expected format
    files = []
    for doc in documents:
        # Generate filename from document type and source
        if doc.source_url:
            filename = f"{doc.type.value}-{doc.id}.txt"
        else:
            filename = f"{doc.type.value}-{doc.id}.{doc.type.value}"
        
        files.append({
            "file_name": filename,
            "size": 0,  # Size would need to be calculated from chunks
            "last_modified": doc.updated_at.isoformat(),
            "etag": str(doc.id),  # Use UUID as etag
            "preview_url": f"/api/documents/{doc.id}"
        })
    
    return {"files": files}


@router.get(
    "/metadata/note/{etag}",
    response_model=NoteResponse,
    summary="Get note by etag",
    description="Get specific note metadata by etag (UUID)"
)
async def get_note_by_etag(
    etag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get note by etag (UUID) - frontend compatibility"""
    from app.features.notes.service import NoteService
    
    try:
        note_id = UUID(etag)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid etag format"
        )
    
    service = NoteService(db, current_user)
    return await service.get_note(note_id)


@router.post(
    "/upload/document",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document file",
    description="Upload document file (Frontend compatibility endpoint)"
)
async def upload_document_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload document file - frontend compatibility wrapper"""
    from app.features.documents.service import DocumentService
    from app.features.documents.processor import DocumentProcessor
    from app.models import DocumentType, DocumentStatus, DocumentChunk
    
    # Determine document type from file extension
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        doc_type = DocumentType.PDF
    elif filename.endswith(('.doc', '.docx')):
        doc_type = DocumentType.WORD
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF and DOC/DOCX are supported."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Create processor and calculate hash
    processor = DocumentProcessor()
    content_hash = processor.calculate_hash(file_content)
    
    # Create document service and record
    service = DocumentService(db, current_user)
    document = await service.create_document(
        doc_type=doc_type,
        content_hash=content_hash
    )
    
    # Process PDF immediately
    if doc_type == DocumentType.PDF:
        try:
            text, chunks = processor.process_pdf(file_content)
            
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Prepare data for batch processing
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:30]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:30]]
            
            # Generate embeddings for all chunks
            embeddings = []
            for text_chunk in chunk_texts:
                embedding = await embedding_service.generate_embedding(text_chunk)
                embeddings.append(embedding)
            
            # Store in Qdrant and get vector IDs
            vector_ids = await vector_db.add_vectors(
                vectors=embeddings,
                texts=chunk_texts,
                document_id=document.id,
                metadata=chunk_metadata
            )
            
            # Store chunk records in PostgreSQL
            for chunk_text, vector_id, metadata in zip(chunk_texts, vector_ids, chunk_metadata):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    vector_id=vector_id,
                    chunk_metadata=metadata
                )
                db.add(chunk)
            
            # Update status to completed
            document.status = DocumentStatus.COMPLETED
            await db.commit()
            await db.refresh(document)
            
        except Exception as e:
            document.status = DocumentStatus.FAILED
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF processing failed: {str(e)}"
            )
    
    # Process DOCX immediately
    elif doc_type == DocumentType.WORD:
        try:
            text, chunks = processor.process_docx(file_content)
            
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Prepare data for batch processing
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:30]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:30]]
            
            # Generate embeddings for all chunks
            embeddings = []
            for text_chunk in chunk_texts:
                embedding = await embedding_service.generate_embedding(text_chunk)
                embeddings.append(embedding)
            
            # Store in Qdrant and get vector IDs
            vector_ids = await vector_db.add_vectors(
                vectors=embeddings,
                texts=chunk_texts,
                document_id=document.id,
                metadata=chunk_metadata
            )
            
            # Store chunk records in PostgreSQL
            for chunk_text, vector_id, metadata in zip(chunk_texts, vector_ids, chunk_metadata):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    vector_id=vector_id,
                    chunk_metadata=metadata
                )
                db.add(chunk)
            
            # Update status to completed
            document.status = DocumentStatus.COMPLETED
            await db.commit()
            await db.refresh(document)
            
        except Exception as e:
            document.status = DocumentStatus.FAILED
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DOCX processing failed: {str(e)}"
            )
    
    return {
        "message": "File uploaded successfully",
        "document_id": str(document.id),
        "etag": str(document.id),  # Frontend expects etag
        "status": document.status.value,
        "file_name": file.filename,
        "type": doc_type.value
    }


@router.get(
    "/document/{etag}/status",
    response_model=dict,
    summary="Get document processing status",
    description="Get document processing status by etag (Frontend compatibility endpoint)"
)
async def get_document_status(
    etag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document processing status - frontend compatibility"""
    from app.features.documents.service import DocumentService
    
    try:
        document_id = UUID(etag)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid etag format"
        )
    
    service = DocumentService(db, current_user)
    document = await service.get_document(document_id)
    
    return {
        "document_id": str(document.id),
        "etag": str(document.id),
        "status": document.status.value,
        "type": document.type.value,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat()
    }
