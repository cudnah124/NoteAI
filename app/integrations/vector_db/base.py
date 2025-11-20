"""
Vector Database base interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID


class VectorDB(ABC):
    """Abstract base class for vector database implementations"""
    
    @abstractmethod
    async def add_vectors(
        self,
        vectors: List[List[float]],
        texts: List[str],
        document_id: UUID,
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """Add vectors to the database"""
        pass
    
    @abstractmethod
    async def search_similar(
        self,
        query_vector: List[float],
        document_id: Optional[UUID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    async def delete_document_vectors(self, document_id: UUID):
        """Delete all vectors associated with a document"""
        pass
