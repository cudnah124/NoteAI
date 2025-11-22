"""
AI service - Business logic for AI features (review, recommendations)
"""
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import User, Note, Document
from app.schemas import ReviewResponse, RecommendationResponse

logger = logging.getLogger(__name__)


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
        
        # Detect language of the note
        note_language = "Vietnamese" if any(ord(c) > 127 for c in note.content[:200]) else "English"
        logger.info(f"Detected note language: {note_language}")
        
        # Create single prompt that requires LLM to respond in the note's language
        review_prompt = f"""You are an expert educational reviewer. Review the following student note based on the original document content.

ORIGINAL DOCUMENT CONTENT:
{document_context[:2000]}

STUDENT'S NOTE:
Title: {note.title}
Content: {note.content}

**CRITICAL INSTRUCTION: The student wrote this note in {note_language}. You MUST respond ENTIRELY in {note_language} language. Do NOT mix languages. Every single word in your response must be in {note_language}.**

Provide a detailed review with the following sections:
1. Overall feedback on the note quality
2. Strengths: What the student did well (2-3 points)
3. Areas for improvement: Specific aspects that need work (2-3 points)
4. Missing concepts: Important concepts from the document that weren't covered (2-4 items)
5. Suggestions to add: Specific content to add from the document (3-5 detailed suggestions)
6. Corrections: Any inaccuracies that need fixing (if any)
7. Additional resources: Related topics to explore further (2-3 items)

Format your response as structured feedback. REMEMBER: Write EVERYTHING in {note_language}. No exceptions."""
        
        if settings.MOCK_MODE:
            # Mock detailed response in the note's language
            if note_language == "Vietnamese":
                review_text = f"""Nhận xét tổng quan: Ghi chú của bạn về '{note.title}' cho thấy nền tảng tốt nhưng cần mở rộng thêm.

Điểm mạnh:
- Cấu trúc rõ ràng với các tiêu đề
- Sử dụng markdown tốt
- Bao gồm các khái niệm cơ bản

Điểm cần cải thiện:
- Thêm các ví dụ cụ thể hơn từ tài liệu nguồn
- Mở rộng các khái niệm chính với định nghĩa
- Bao gồm ứng dụng thực tế

Khái niệm còn thiếu:
- Các kỹ thuật nâng cao được đề cập trong tài liệu
- Các trường hợp sử dụng thực tế
- Thực hành tốt nhất và những lỗi thường gặp

Gợi ý bổ sung:
1. Thêm phần giải thích các nguyên tắc cốt lõi với ví dụ từ tài liệu
2. Bao gồm sơ đồ hoặc biểu diễn trực quan nếu được đề cập trong nguồn
3. Thêm ví dụ code hoặc minh họa thực tế
4. Tóm tắt những điểm chính ở cuối
5. Tham chiếu chéo các khái niệm liên quan

Sửa lỗi:
- Làm rõ định nghĩa trong đoạn 2
- Cập nhật ví dụ để phù hợp với cách tiếp cận của tài liệu

Tài liệu tham khảo thêm:
- Khám phá các chủ đề nâng cao được đề cập trong phần 3
- Nghiên cứu các ứng dụng thực tế được thảo luận
- Xem lại các nghiên cứu điển hình được cung cấp"""
            else:
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
            logger.info(f"LLM response preview (first 200 chars): {review_text[:200]}")
        
        # Parse review text into structured response
        def extract_section(text: str, *section_names: str) -> list:
            """Extract content from a section (supports multiple language variants)"""
            lines = text.split('\n')
            items = []
            in_section = False
            section_start_idx = -1
            
            # Find section start
            for i, line in enumerate(lines):
                if any(section_name.lower() in line.lower() for section_name in section_names):
                    in_section = True
                    section_start_idx = i
                    continue
                    
                if in_section:
                    stripped = line.strip()
                    
                    # Stop at next section (line ending with : or starting with number and period)
                    if stripped.endswith(':') and i > section_start_idx + 1:
                        break
                        
                    # Extract item (bullet, dash, number, or any non-empty line)
                    if stripped:
                        # Remove common prefixes
                        for prefix in ['-', '•', '*', '–']:
                            if stripped.startswith(prefix):
                                stripped = stripped[1:].strip()
                                break
                        
                        # Handle numbered items (1., 2., etc)
                        if stripped and stripped[0].isdigit():
                            parts = stripped.split('.', 1)
                            if len(parts) > 1:
                                stripped = parts[1].strip()
                        
                        if stripped:
                            items.append(stripped)
                    
            return items
        
        # Extract overall feedback (first paragraph before any section)
        overall_markers = ["Strengths:", "Điểm mạnh:", "2.", "Areas", "Điểm cần"]
        overall_lines = []
        for line in review_text.split('\n'):
            if any(marker in line for marker in overall_markers):
                break
            if line.strip():
                overall_lines.append(line.strip())
        
        overall = ' '.join(overall_lines[:3]) if overall_lines else review_text[:200]
        overall = overall.replace("Overall:", "").replace("Nhận xét tổng quan:", "").replace("1.", "").strip()
        
        strengths = extract_section(review_text, "Strengths:", "Điểm mạnh:", "2.")
        improvements = extract_section(review_text, "Areas for improvement:", "Điểm cần cải thiện:", "3.")
        missing = extract_section(review_text, "Missing concepts:", "Khái niệm còn thiếu:", "Khái niệm bị thiếu:", "4.")
        suggestions = extract_section(review_text, "Suggestions to add:", "Gợi ý bổ sung:", "5.")
        
        # Parse corrections (supports both languages)
        corrections = []
        if "Corrections:" in review_text or "Sửa lỗi:" in review_text:
            corr_marker = "Corrections:" if "Corrections:" in review_text else "Sửa lỗi:"
            resource_marker = "Additional resources:" if "Additional resources:" in review_text else "Tài liệu tham khảo thêm:"
            
            if resource_marker in review_text:
                corr_section = review_text.split(corr_marker)[1].split(resource_marker)[0]
            else:
                corr_section = review_text.split(corr_marker)[1]
            
            corr_items = extract_section(review_text, "Corrections:", "Sửa lỗi:")
            for item in corr_items:
                corrections.append({"issue": item, "correction": "See feedback above"})
        
        resources = extract_section(review_text, "Additional resources:", "Tài liệu tham khảo thêm:")
        
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
        
        # Get document chunks for context
        from app.models import DocumentChunk
        chunks_result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id).limit(5)
        )
        chunks = chunks_result.scalars().all()
        document_context = "\n".join([chunk.content for chunk in chunks]) if chunks else "No document content available"
        
        # Detect language from notes
        note_language = "Vietnamese"
        if user_notes:
            combined_notes = " ".join([note.content for note in user_notes])
            if not any(ord(c) > 127 for c in combined_notes[:500]):
                note_language = "English"
        
        logger.info(f"Detected note language for recommendations: {note_language}")
        
        # Generate recommendations using LLM
        from app.integrations.naver.hyperclova import HyperCLOVAService
        from app.core.config import settings
        
        llm = HyperCLOVAService()
        
        notes_summary = "\n".join([f"- {note.title}: {note.content[:200]}..." for note in user_notes]) if user_notes else "No notes created yet"
        
        rec_prompt = f"""You are an expert educational advisor. Analyze the document content and user's study notes to provide recommendations.

DOCUMENT CONTENT:
{document_context[:2000]}

USER'S NOTES:
{notes_summary}

**CRITICAL: The user wrote notes in {note_language}. You MUST respond ENTIRELY in {note_language}. Do NOT mix languages.**

Provide study recommendations with:
1. Coverage assessment: What percentage of material has been covered (estimate)
2. Missing sections: Key topics from the document not yet covered (3-5 items)
3. Suggested topics: Specific topics to study next (3-5 detailed suggestions)
4. Overall recommendation: Brief advice on how to proceed

Write EVERYTHING in {note_language}. Format as clear sections."""

        if settings.MOCK_MODE:
            if note_language == "Vietnamese":
                rec_text = """Đánh giá độ bao phủ: Bạn đã bao phủ khoảng 30% tài liệu.

Các phần còn thiếu:
- Các kỹ thuật nâng cao chưa được đề cập
- Ví dụ thực tế và ứng dụng
- Các bài tập thực hành
- Phân tích chuyên sâu về các khái niệm phức tạp

Chủ đề được đề xuất:
- Tìm hiểu sâu hơn về các nguyên tắc cốt lõi
- Nghiên cứu các trường hợp sử dụng thực tế
- Thực hành với các ví dụ mã
- Đọc thêm tài liệu bổ sung về chủ đề này

Khuyến nghị tổng thể: Tập trung vào các phần còn thiếu để hoàn thiện kiến thức. Nên làm thêm bài tập thực hành."""
            else:
                rec_text = """Coverage assessment: You have covered approximately 30% of the material.

Missing sections:
- Advanced techniques not yet covered
- Real-world examples and applications
- Practical exercises
- In-depth analysis of complex concepts

Suggested topics:
- Deep dive into core principles
- Research real-world use cases
- Practice with code examples
- Read supplementary materials on this topic

Overall recommendation: Focus on the missing sections to complete your understanding. Consider doing more practical exercises."""
        else:
            messages = [
                {"role": "system", "content": "You are an expert educational advisor providing study recommendations."},
                {"role": "user", "content": rec_prompt}
            ]
            rec_text = await llm.chat_completion(messages, temperature=0.7, max_tokens=1500)
            logger.info(f"Recommendations response preview (first 200 chars): {rec_text[:200]}")
        
        # Parse recommendations
        def extract_list_items(text: str, *markers: str) -> list:
            """Extract list items after a marker"""
            lines = text.split('\n')
            items = []
            in_section = False
            
            for line in lines:
                if any(marker.lower() in line.lower() for marker in markers):
                    in_section = True
                    continue
                
                if in_section:
                    stripped = line.strip()
                    if stripped.endswith(':') or (stripped and any(m in stripped for m in ["Coverage", "Đánh giá", "Overall", "Khuyến nghị"])):
                        break
                    
                    if stripped:
                        for prefix in ['-', '•', '*', '–']:
                            if stripped.startswith(prefix):
                                stripped = stripped[1:].strip()
                                break
                        
                        if stripped and stripped[0].isdigit():
                            parts = stripped.split('.', 1)
                            if len(parts) > 1:
                                stripped = parts[1].strip()
                        
                        if stripped:
                            items.append(stripped)
            
            return items
        
        # Extract coverage percentage
        coverage = 30.0  # Default
        for line in rec_text.split('\n'):
            if any(word in line.lower() for word in ['coverage', 'đánh giá', 'bao phủ', '%']):
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    coverage = float(numbers[0])
                    break
        
        missing = extract_list_items(rec_text, "Missing sections:", "Các phần còn thiếu:", "Phần còn thiếu:")
        suggested = extract_list_items(rec_text, "Suggested topics:", "Chủ đề được đề xuất:", "Đề xuất:")
        
        # Extract overall recommendation
        overall_lines = []
        for line in rec_text.split('\n'):
            if any(m in line for m in ["Overall recommendation:", "Khuyến nghị tổng thể:"]):
                idx = rec_text.index(line)
                overall_lines = rec_text[idx:].split('\n')[1:3]
                break
        
        overall_rec = ' '.join([l.strip() for l in overall_lines if l.strip()]) if overall_lines else rec_text[-200:]
        
        return RecommendationResponse(
            document_id=document_id,
            missing_sections=missing if missing else ["Review document for missing topics"],
            suggested_topics=suggested if suggested else ["Study core concepts"],
            coverage_percentage=coverage,
            recommendations=overall_rec if overall_rec else f"Continue studying to improve coverage (currently {coverage:.0f}%)"
        )
