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
    print(f"🟢 UPLOAD STARTED: filename={filename}", flush=True)
    
    if filename.endswith('.pdf'):
        doc_type = DocumentType.PDF
    elif filename.endswith(('.docx', '.doc')):
        doc_type = DocumentType.WORD
        print(f"🟢 File type detected: WORD", flush=True)
    elif filename.endswith(('.jpg', '.jpeg', '.png')):
        doc_type = DocumentType.IMAGE
    elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        doc_type = DocumentType.VIDEO
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF, DOCX, images, and videos are supported."
        )
    
    print(f"🟢 doc_type={doc_type}, DocumentType.WORD={DocumentType.WORD}, Equal? {doc_type == DocumentType.WORD}", flush=True)
    
    # Read file content
    file_content = await file.read()
    
    # Calculate hash
    content_hash = processor.calculate_hash(file_content)
    
    # Create document record
    document = await service.create_document(
        doc_type=doc_type,
        content_hash=content_hash
    )
    
    print(f"🔷 Document created: {document.id}, type={doc_type}, status={document.status}", flush=True)

    # Process video files immediately using Whisper
    if doc_type == DocumentType.VIDEO:
        print(f"🔷 Processing VIDEO: {document.id}", flush=True)
        try:
            text, chunks = await processor.process_video(file_content)
            
            # Import required services
            from app.models import DocumentChunk
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Prepare data for batch processing
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:20]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:20]]
            
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
                detail=f"Video processing failed: {str(e)}"
            )
    
    # Process PDF files immediately
    elif doc_type == DocumentType.PDF:
        print(f"🟡 PDF PROCESSING: {document.id}", flush=True)
        try:
            print(f"🟡 Calling process_pdf() for {document.id}", flush=True)
            text, chunks = processor.process_pdf(file_content)
            
            # Import required services
            from app.models import DocumentChunk
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
                detail=f"PDF processing failed: {str(e)}"
            )
    
    # Process DOCX/Word files immediately
    elif doc_type == DocumentType.WORD:
        print(f"🔷 Processing DOCX: {document.id}", flush=True)
        try:
            print(f"🔷 Calling process_docx() for {document.id}", flush=True)
            text, chunks = processor.process_docx(file_content)
            print(f"🔷 process_docx() returned {len(chunks)} chunks for {document.id}", flush=True)
            
            # Import required services
            from app.models import DocumentChunk
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
                service.db.add(chunk)
            
            # Update status to completed
            document.status = DocumentStatus.COMPLETED
            await service.db.commit()
            await service.db.refresh(document)
            print(f"🔵 DOCX COMPLETED: {document.id}", flush=True)
            
        except Exception as e:
            print(f"🔴 DOCX FAILED: {document.id}, error: {str(e)}", flush=True)
            document.status = DocumentStatus.FAILED
            await service.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DOCX processing failed: {str(e)}"
            )
    
    # TODO: For other document types, trigger async processing task
    # from app.tasks import process_document_task
    # process_document_task.delay(str(document.id), file_content, doc_type.value)
    
    print(f"🟢 RETURNING document {document.id} with status={document.status}", flush=True)
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
            
            # Import required services
            from app.models import DocumentChunk
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Prepare data for batch processing
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:10]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:10]]
            
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
    
    # For Web URLs, process immediately using BeautifulSoup
    elif doc_data.type == DocumentType.WEB:
        try:
            text, chunks = await processor.process_web_url(str(doc_data.source_url))
            
            # Import required services
            from app.models import DocumentChunk
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Prepare data for batch processing (limit to first 20 chunks for speed)
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:20]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:20]]
            
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
                service.db.add(chunk)
            
            # Update status to completed
            document.status = DocumentStatus.COMPLETED
            await service.db.commit()
            await service.db.refresh(document)
            
        except Exception as e:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            await service.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Web processing failed: {str(e)}"
            )
    
    # For PDF URLs, create mock content for demo (TODO: implement real PDF download & processing)
    elif doc_data.type == DocumentType.PDF:
        try:
            # Import required services
            from app.models import DocumentChunk
            from app.integrations.naver import embedding_service
            from app.integrations.vector_db import vector_db
            
            # Create mock PDF content for testing
            mock_content = f"""# Machine Learning Document

This is a comprehensive guide about machine learning fundamentals. 

## Introduction
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Key Concepts
1. **Supervised Learning**: Training models with labeled data
2. **Unsupervised Learning**: Finding patterns in unlabeled data
3. **Neural Networks**: Computing systems inspired by biological neural networks
4. **Deep Learning**: ML methods based on artificial neural networks with representation learning

## Applications
Machine learning has numerous applications including image recognition, natural language processing, recommendation systems, and autonomous vehicles.

Document source: {doc_data.source_url}"""
            
            chunks = processor.chunk_text(mock_content, metadata={"type": "pdf", "source": "url"})
            
            # Prepare data for batch processing
            chunk_texts = [chunk_data["content"] for chunk_data in chunks[:15]]
            chunk_metadata = [chunk_data.get("metadata", {}) for chunk_data in chunks[:15]]
            
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
                detail=f"PDF processing failed: {str(e)}"
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
