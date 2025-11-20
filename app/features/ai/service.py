"""
AI service - Business logic for AI features (review, recommendations)
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Note, Document
from app.schemas import ReviewResponse, RecommendationResponse


class AIService:
    """Service class for AI-powered features"""
    
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
    
    async def review_note(self, note_id: UUID) -> ReviewResponse:
        """
        Review a note and provide detailed feedback based on document content
        
        Args:
            note_id: Note UUID
            
        Returns:
            Review response with detailed feedback and suggestions
            
        Raises:
            HTTPException: If note not found
        """
        # Get note and verify access
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
        
        # Get associated document
        doc_result = await self.db.execute(
            select(Document).where(Document.id == note.document_id)
        )
        document = doc_result.scalar_one_or_none()
        
        # Get document chunks for context
        from app.models import DocumentChunk
        chunks_result = await self.db.execute(
            select(DocumentChunk).where(
                DocumentChunk.document_id == note.document_id
            ).limit(10)
        )
        chunks = chunks_result.scalars().all()
        
        # Prepare context from document
        document_context = "\n".join([chunk.content for chunk in chunks]) if chunks else "No document content available"
        
        # Use HyperCLOVA to generate detailed review
        from app.integrations.naver.hyperclova import HyperCLOVAService
        from app.core.config import settings
        
        llm = HyperCLOVAService()
        
        # Create prompt for detailed review
        review_prompt = f"""You are an expert educational reviewer. Review the following student note based on the original document content.

ORIGINAL DOCUMENT CONTENT:
{document_context[:2000]}

STUDENT'S NOTE:
Title: {note.title}
Content: {note.content}

Provide a detailed review with the following:
1. Overall feedback on the note quality
2. Strengths: What the student did well (2-3 points)
3. Areas for improvement: Specific aspects that need work (2-3 points)
4. Missing concepts: Important concepts from the document that weren't covered (2-4 items)
5. Suggestions to add: Specific content to add from the document (3-5 detailed suggestions)
6. Corrections: Any inaccuracies that need fixing (if any)
7. Additional resources: Related topics to explore further (2-3 items)

Format your response as structured feedback that helps the student improve their understanding."""
        
        if settings.MOCK_MODE:
            # Mock detailed response
            review_text = f"""Overall: Your note on '{note.title}' shows a good foundation but needs expansion.

Strengths:
- Clear structure with headings
- Good use of markdown formatting
- Covers basic concepts

Areas for improvement:
- Add more specific examples from the source material
- Expand on key concepts with definitions
- Include practical applications

Missing concepts:
- Advanced techniques mentioned in the document
- Real-world use cases
- Best practices and common pitfalls

Suggestions to add:
1. Add a section explaining the core principles with examples from the document
2. Include diagrams or visual representations if mentioned in source
3. Add code examples or practical demonstrations
4. Summarize the key takeaways at the end
5. Cross-reference related concepts

Corrections:
- Clarify the definition in paragraph 2
- Update the example to match the document's approach

Additional resources:
- Explore the advanced topics mentioned in section 3
- Research the practical applications discussed
- Review the case studies provided"""
        else:
            messages = [
                {"role": "system", "content": "You are an expert educational reviewer providing detailed, constructive feedback."},
                {"role": "user", "content": review_prompt}
            ]
            review_text = await llm.chat_completion(messages, temperature=0.7, max_tokens=2000)
        
        # Parse review text into structured response
        def extract_section(text: str, section_name: str) -> list:
            """Extract bullet points from a section"""
            lines = text.split('\n')
            items = []
            in_section = False
            for line in lines:
                if section_name in line:
                    in_section = True
                    continue
                if in_section:
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        items.append(line.strip()[1:].strip())
                    elif line.strip() and line.strip()[0].isdigit() and '.' in line[:3]:
                        items.append(line.split('.', 1)[1].strip())
                    elif line.strip() and not line[0].isspace() and items:
                        break
            return items
        
        overall = review_text.split("Strengths:")[0].replace("Overall:", "").strip() if "Strengths:" in review_text else review_text[:200]
        strengths = extract_section(review_text, "Strengths:")
        improvements = extract_section(review_text, "Areas for improvement:")
        missing = extract_section(review_text, "Missing concepts:")
        suggestions = extract_section(review_text, "Suggestions to add:")
        
        # Parse corrections
        corrections = []
        if "Corrections:" in review_text:
            corr_section = review_text.split("Corrections:")[1].split("Additional resources:")[0] if "Additional resources:" in review_text else review_text.split("Corrections:")[1]
            corr_items = extract_section(review_text, "Corrections:")
            for item in corr_items:
                corrections.append({"issue": item, "correction": "See feedback above"})
        
        resources = extract_section(review_text, "Additional resources:")
        
        return ReviewResponse(
            note_id=note_id,
            overall_feedback=overall,
            strengths=strengths if strengths else ["Clear structure with headings"],
            areas_for_improvement=improvements if improvements else ["Add more details"],
            missing_concepts=missing if missing else ["See document for missing topics"],
            suggestions_to_add=suggestions if suggestions else ["Review document content"],
            corrections=corrections if corrections else [],
            additional_resources=resources if resources else ["Review related materials"]
        )
    
    async def generate_recommendations(self, document_id: UUID) -> RecommendationResponse:
        """
        Generate study recommendations based on user's notes
        
        Args:
            document_id: Document UUID
            
        Returns:
            Recommendation response with suggested topics
            
        Raises:
            HTTPException: If document not found
        """
        # Verify document access
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
        
        # Get user's notes for this document
        notes_result = await self.db.execute(
            select(Note).where(
                Note.document_id == document_id,
                Note.user_id == self.current_user.id
            )
        )
        user_notes = notes_result.scalars().all()
        
        # TODO: Implement AI recommendations using HyperCLOVA
        # 1. Analyze document content
        # 2. Compare with user's notes
        # 3. Identify gaps and suggest topics
        
        # Placeholder response
        coverage = (len(user_notes) / 10) * 100 if len(user_notes) < 10 else 100
        
        return RecommendationResponse(
            document_id=document_id,
            missing_sections=[
                "Advanced Topics",
                "Practical Examples"
            ],
            suggested_topics=[
                "Deep dive into core concepts",
                "Real-world applications"
            ],
            coverage_percentage=coverage,
            recommendations=f"You have covered {coverage:.0f}% of the material. Focus on the missing sections to complete your understanding."
        )
