"""
HyperCLOVA X AI Service - Naver Cloud Platform Integration
"""
import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from app.integrations.naver.base import NaverBaseClient

logger = logging.getLogger(__name__)


class HyperCLOVAService(NaverBaseClient):
    """Service for interacting with HyperCLOVA X API"""
    
    def __init__(self):
        from app.core.config import settings
        self.mock_mode = settings.MOCK_MODE
        super().__init__(
            api_url=settings.HYPERCLOVA_API_URL,
            api_key=settings.HYPERCLOVA_API_KEY
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate chat completion using HyperCLOVA X
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        if self.mock_mode:
            logger.info(f"MOCK_MODE: Generating mock chat response for {len(messages)} messages")
            last_msg = messages[-1]['content'] if messages else "No message"
            return f"This is a mock AI response to: '{last_msg[:100]}...' Based on the provided context, I can help you understand the key concepts and main topics covered in the document."
        
        payload = {
            "messages": messages,
            "topP": 0.8,
            "topK": 0,
            "maxTokens": max_tokens,
            "temperature": temperature,
            "repeatPenalty": 5.0,
            "stopBefore": [],
            "includeAiFilters": True
        }
        
        result = await self._make_request("POST", "", json=payload)
        return result["result"]["message"]["content"]
    
    async def qa_with_context(
        self,
        question: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Answer question based on context chunks
        
        Args:
            question: User's question
            context_chunks: Retrieved document chunks
            chat_history: Optional previous chat messages
            
        Returns:
            Answer string
        """
        context = "\n\n".join(context_chunks)
        
        system_message = f"""Dựa vào thông tin sau từ tài liệu:

{context}

Hãy trả lời câu hỏi của người dùng một cách chính xác và chi tiết.
Nếu không tìm thấy thông tin trong tài liệu, hãy nói "Tôi không tìm thấy thông tin này trong tài liệu"."""
        
        messages = [{"role": "system", "content": system_message}]
        
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": question})
        
        return await self.chat_completion(messages)
    
    async def review_note(
        self,
        user_note: str,
        source_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        Review and critique user's note against source material
        
        Args:
            user_note: User's note content
            source_chunks: Relevant chunks from source document
            
        Returns:
            Review result as dictionary
        """
        source_text = "\n\n".join(source_chunks)
        
        system_message = """Bạn là một giáo viên phản biện chuyên nghiệp."""
        
        user_message = f"""[Source Material]:
{source_text}

[Student Note]:
{user_note}

[Task]:
So sánh ghi chú của học sinh với tài liệu gốc. Chỉ ra các điểm sai lầm, hiểu nhầm, và những điểm quan trọng bị thiếu.

Trả về kết quả dưới dạng JSON hợp lệ với format sau:
{{
  "correctness_score": <số từ 0-10>,
  "misunderstandings": ["danh sách các hiểu nhầm"],
  "missing_points": ["danh sách các điểm quan trọng bị thiếu"],
  "constructive_feedback": "nhận xét mang tính xây dựng"
}}

CHỈ trả về JSON, không thêm text nào khác."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        response = await self.chat_completion(messages, temperature=0.3)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {
                "correctness_score": 5,
                "misunderstandings": [],
                "missing_points": [],
                "constructive_feedback": response
            }
    
    async def generate_recommendations(
        self,
        user_notes: List[str],
        document_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        Generate personalized study recommendations
        
        Args:
            user_notes: List of user's notes
            document_chunks: All chunks from the document
            
        Returns:
            Recommendations as dictionary
        """
        notes_summary = "\n".join(user_notes)
        doc_summary = "\n".join(document_chunks[:10])  # Sample of document
        
        system_message = """Bạn là một trợ lý học tập AI."""
        
        user_message = f"""[Document Content]:
{doc_summary}

[Student's Current Notes]:
{notes_summary}

[Task]:
Phân tích những gì học sinh đã học và đưa ra đề xuất về những phần cần học thêm.

Trả về JSON hợp lệ với format sau:
{{
  "missing_sections": ["các phần quan trọng chưa học"],
  "suggested_topics": ["các chủ đề nên tìm hiểu thêm"],
  "coverage_percentage": <số từ 0-100>,
  "recommendations": "lời khuyên chi tiết"
}}

CHỈ trả về JSON, không thêm text nào khác."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        response = await self.chat_completion(messages, temperature=0.5)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {
                "missing_sections": [],
                "suggested_topics": [],
                "coverage_percentage": 50,
                "recommendations": response
            }


# Singleton instance
hyperclova_service = HyperCLOVAService()
