"""
RAG (Retrieval Augmented Generation) Engine
Orchestrates retrieval and generation for Q&A
"""
from typing import List, Dict, Any
from uuid import UUID


class RAGEngine:
    """RAG engine for context-aware question answering"""
    
    def __init__(self):
        # Lazy import to avoid circular dependencies
        from app.integrations.naver import embedding_service, hyperclova_service
        from app.integrations.vector_db import vector_db
        
        self.embedding_service = embedding_service
        self.vector_db = vector_db
        self.llm_service = hyperclova_service
    
    async def retrieve_context(
        self,
        query: str,
        document_id: UUID | None = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User's query text
            document_id: Optional filter by document
            top_k: Number of chunks to retrieve
            
        Returns:
            List of retrieved chunks with metadata
        """
        # Generate query embedding
        query_vector = await self.embedding_service.generate_embedding(query)
        
        # Search vector database
        results = await self.vector_db.search_similar(
            query_vector=query_vector,
            document_id=document_id,
            limit=top_k
        )
        
        return results
    
    async def answer_question(
        self,
        question: str,
        document_id: UUID,
        chat_history: List[Dict[str, str]] | None = None
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            document_id: Document to search in
            chat_history: Previous chat messages
            
        Returns:
            Tuple of (answer, retrieved_chunks)
        """
        # Retrieve relevant context
        retrieved = await self.retrieve_context(
            query=question,
            document_id=document_id,
            top_k=5
        )
        
        # Extract text chunks
        context_chunks = [item.get("text", "") for item in retrieved]
        
        # Generate answer using LLM with context
        answer = await self.llm_service.qa_with_context(
            question=question,
            context_chunks=context_chunks,
            chat_history=chat_history
        )
        
        return answer, retrieved


# Singleton instance
rag_engine = RAGEngine()
