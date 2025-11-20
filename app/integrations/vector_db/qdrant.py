"""
Qdrant Vector Database Service
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from .base import VectorDB


class QdrantService(VectorDB):
    """Service for managing vector database operations with Qdrant"""
    
    def __init__(self):
        from app.core.config import settings
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists, create if not"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1024,  # Clova Embedding dimension
                    distance=Distance.COSINE
                )
            )
    
    async def add_vectors(
        self,
        vectors: List[List[float]],
        texts: List[str],
        document_id: UUID,
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add vectors to the database
        
        Args:
            vectors: List of embedding vectors
            texts: List of text chunks
            document_id: Document UUID
            metadata: List of metadata dictionaries
            
        Returns:
            List of vector IDs
        """
        vector_ids = []
        points = []
        
        for i, (vector, text, meta) in enumerate(zip(vectors, texts, metadata)):
            vector_id = str(uuid4())
            vector_ids.append(vector_id)
            
            points.append(
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload={
                        "text": text,
                        "document_id": str(document_id),
                        "metadata": meta
                    }
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return vector_ids
    
    async def search_similar(
        self,
        query_vector: List[float],
        document_id: Optional[UUID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            document_id: Optional filter by document ID
            limit: Number of results to return
            
        Returns:
            List of search results with text and metadata
        """
        query_filter = None
        if document_id:
            query_filter = {
                "must": [
                    {
                        "key": "document_id",
                        "match": {"value": str(document_id)}
                    }
                ]
            }
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text"),
                "metadata": result.payload.get("metadata"),
                "document_id": result.payload.get("document_id")
            }
            for result in results
        ]
    
    async def delete_document_vectors(self, document_id: UUID):
        """Delete all vectors associated with a document"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "document_id",
                            "match": {"value": str(document_id)}
                        }
                    ]
                }
            }
        )


# Singleton instance
vector_db = QdrantService()
