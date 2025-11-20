"""
Notes API routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core import get_db, get_current_user
from app.models import User
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from .service import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])


def get_note_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NoteService:
    """Dependency to get note service instance"""
    return NoteService(db, current_user)


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new study note linked to a document"
)
async def create_note(
    note_data: NoteCreate,
    service: NoteService = Depends(get_note_service)
):
    """Create a new note"""
    return await service.create_note(note_data)


@router.get(
    "/",
    response_model=list[NoteResponse],
    summary="List notes",
    description="Get all notes for current user, optionally filtered by document"
)
async def list_notes(
    document_id: UUID | None = Query(None, description="Filter by document ID"),
    service: NoteService = Depends(get_note_service)
):
    """List user's notes"""
    return await service.list_notes(document_id)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get note",
    description="Get a specific note by ID"
)
async def get_note(
    note_id: UUID,
    service: NoteService = Depends(get_note_service)
):
    """Get a specific note"""
    return await service.get_note(note_id)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update note",
    description="Update note title or content"
)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    service: NoteService = Depends(get_note_service)
):
    """Update a note"""
    return await service.update_note(note_id, note_data)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note permanently"
)
async def delete_note(
    note_id: UUID,
    service: NoteService = Depends(get_note_service)
):
    """Delete a note"""
    await service.delete_note(note_id)
