"""
AI API routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core import get_db, get_current_user
from app.models import User
from app.schemas import ReviewRequest, ReviewResponse, RecommendationResponse
from .service import AIService

router = APIRouter(prefix="/ai", tags=["AI Services"])


def get_ai_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AIService:
    """Dependency to get AI service instance"""
    return AIService(db, current_user)


@router.post(
    "/review",
    response_model=ReviewResponse,
    summary="Review note",
    description="AI-powered review of user's note with correctness score and feedback"
)
async def review_note(
    request: ReviewRequest,
    service: AIService = Depends(get_ai_service)
):
    """Review a note and provide constructive feedback"""
    return await service.review_note(request.note_id)


@router.get(
    "/recommend/{document_id}",
    response_model=RecommendationResponse,
    summary="Get study recommendations",
    description="AI-powered study recommendations based on user's learning progress"
)
async def get_recommendations(
    document_id: UUID,
    service: AIService = Depends(get_ai_service)
):
    """Generate personalized study recommendations"""
    return await service.generate_recommendations(document_id)
