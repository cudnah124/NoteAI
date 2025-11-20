"""
Chat API routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core import get_db, get_current_user
from app.models import User
from app.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse
)
from .service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat & Q&A"])


def get_chat_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatService:
    """Dependency to get chat service instance"""
    return ChatService(db, current_user)


@router.post(
    "/session",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat session",
    description="Create a new chat session for Q&A with a document"
)
async def create_chat_session(
    session_data: ChatSessionCreate,
    service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    return await service.create_session(session_data)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send message",
    description="Send a message and get AI response using RAG"
)
async def send_message(
    message_data: ChatMessageCreate,
    service: ChatService = Depends(get_chat_service)
):
    """Send a message in a chat session"""
    return await service.send_message(message_data)


@router.get(
    "/session/{session_id}/messages",
    response_model=list[ChatMessageResponse],
    summary="Get chat history",
    description="Get all messages in a chat session"
)
async def get_session_messages(
    session_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    """Get all messages in a chat session"""
    return await service.get_chat_history(session_id)


@router.get(
    "/sessions",
    response_model=list[ChatSessionResponse],
    summary="List chat sessions",
    description="Get all chat sessions for current user"
)
async def list_sessions(
    document_id: UUID | None = Query(None, description="Filter by document ID"),
    service: ChatService = Depends(get_chat_service)
):
    """List all chat sessions"""
    return await service.list_sessions(document_id)


@router.delete(
    "/session/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete chat session",
    description="Delete a chat session and all its messages"
)
async def delete_session(
    session_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session"""
    await service.delete_session(session_id)
