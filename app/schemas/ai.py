"""
AI service-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from uuid import UUID


class ReviewRequest(BaseModel):
    """Schema for AI review request"""
    note_id: UUID


class ReviewResponse(BaseModel):
    """Schema for AI review response with detailed feedback"""
    note_id: UUID
    overall_feedback: str = Field(..., description="Overall assessment of the note")
    strengths: list[str] = Field(default_factory=list, description="What's done well in the note")
    areas_for_improvement: list[str] = Field(default_factory=list, description="Specific areas that need work")
    missing_concepts: list[str] = Field(default_factory=list, description="Important concepts from document not covered")
    suggestions_to_add: list[str] = Field(default_factory=list, description="Specific content to add based on document")
    corrections: list[dict] = Field(default_factory=list, description="Corrections needed with explanations")
    additional_resources: list[str] = Field(default_factory=list, description="Suggested topics to explore further")


class RecommendationResponse(BaseModel):
    """Schema for study recommendations"""
    document_id: UUID
    missing_sections: list[str] = Field(default_factory=list, description="Sections not yet studied")
    suggested_topics: list[str] = Field(default_factory=list, description="Recommended topics to study")
    coverage_percentage: float = Field(..., ge=0, le=100, description="Percentage of material covered")
    recommendations: str = Field(..., description="Personalized study recommendations")
