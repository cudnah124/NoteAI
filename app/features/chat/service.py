"""
Chat service - Business logic for chat sessions and messages
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Document, ChatSession, ChatMessage, MessageRole
from app.schemas import ChatSessionCreate, ChatMessageCreate
from .rag_engine import rag_engine


class ChatService:
    """Service class for chat operations"""
    
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
    
    async def create_session(self, session_data: ChatSessionCreate) -> ChatSession:
        """
        Create a new chat session
        
        Args:
            session_data: Chat session creation data
            
        Returns:
            Created chat session model
            
        Raises:
            HTTPException: If document not found or doesn't belong to user
        """
        # Verify document exists and belongs to user
        result = await self.db.execute(
            select(Document).where(
                Document.id == session_data.document_id,
                Document.user_id == self.current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        # Create session
        session = ChatSession(
            user_id=self.current_user.id,
            document_id=session_data.document_id
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def send_message(self, message_data: ChatMessageCreate) -> ChatMessage:
        """
        Send a message in a chat session
        
        Args:
            message_data: Message creation data
            
        Returns:
            AI response message
            
        Raises:
            HTTPException: If session not found
        """
        # Get session and verify access
        result = await self.db.execute(
            select(ChatSession)
            .join(Document)
            .where(
                ChatSession.id == message_data.session_id,
                Document.user_id == self.current_user.id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Save user message
        user_message = ChatMessage(
            session_id=message_data.session_id,
            role=MessageRole.USER,
            content=message_data.content
        )
        self.db.add(user_message)
        await self.db.commit()
        
        # Get chat history
        chat_history = await self.get_chat_history(message_data.session_id)
        
        # Generate AI response using RAG
        answer, _ = await rag_engine.answer_question(
            question=message_data.content,
            document_id=session.document_id,
            chat_history=[
                {"role": msg.role.value, "content": msg.content}
                for msg in chat_history[:-1]  # Exclude current message
            ]
        )
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=message_data.session_id,
            role=MessageRole.ASSISTANT,
            content=answer
        )
        self.db.add(ai_message)
        await self.db.commit()
        await self.db.refresh(ai_message)
        
        return ai_message
    
    async def get_chat_history(self, session_id: UUID) -> list[ChatMessage]:
        """Get all messages in a chat session"""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()
    
    async def list_sessions(self, document_id: UUID | None = None) -> list[ChatSession]:
        """List all chat sessions for current user"""
        query = (
            select(ChatSession)
            .join(Document)
            .where(Document.user_id == self.current_user.id)
        )
        
        if document_id:
            query = query.where(ChatSession.document_id == document_id)
        
        query = query.order_by(ChatSession.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_session(self, session_id: UUID) -> None:
        """Delete a chat session"""
        result = await self.db.execute(
            select(ChatSession)
            .join(Document)
            .where(
                ChatSession.id == session_id,
                Document.user_id == self.current_user.id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        await self.db.delete(session)
        await self.db.commit()
