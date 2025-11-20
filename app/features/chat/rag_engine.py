"""
RAG (Retrieval Augmented Generation) Engine
Orchestrates retrieval and generation for Q&A
"""
import logging
from typing import List, Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)


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
        logger.info(f"RAG: Retrieving context for query: '{query[:100]}...' from document: {document_id}")
        
        # Generate query embedding
        query_vector = await self.embedding_service.generate_embedding(query)
        logger.info(f"RAG: Generated query embedding, vector length: {len(query_vector)}")
        
        # Search vector database
        results = await self.vector_db.search_similar(
            query_vector=query_vector,
            document_id=document_id,
            limit=top_k
        )
        
        logger.info(f"RAG: Retrieved {len(results)} chunks from vector DB")
        if results:
            logger.info(f"RAG: First chunk preview: {results[0].get('text', '')[:200]}...")
        else:
            logger.warning(f"RAG: No chunks found for document {document_id}")
        
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
        logger.info(f"RAG: Answering question for document {document_id}")
        
        # Retrieve relevant context
        retrieved = await self.retrieve_context(
            query=question,
            document_id=document_id,
            top_k=5
        )
        
        # Extract text chunks
        context_chunks = [item.get("text", "") for item in retrieved]
        logger.info(f"RAG: Extracted {len(context_chunks)} text chunks, total chars: {sum(len(c) for c in context_chunks)}")
        
        # Generate answer using LLM with context
        answer = await self.llm_service.qa_with_context(
            question=question,
            context_chunks=context_chunks,
            chat_history=chat_history
        )
        
        logger.info(f"RAG: Generated answer length: {len(answer)} chars")
        return answer, retrieved


# Singleton instance
rag_engine = RAGEngine()
