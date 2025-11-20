"""
Naver Clova Embedding Service - Naver Cloud Platform Integration
"""
from typing import List
from uuid import uuid4
import hashlib
import logging

from app.integrations.naver.base import NaverBaseClient

logger = logging.getLogger(__name__)


class EmbeddingService(NaverBaseClient):
    """Service for generating embeddings using Clova Embedding API"""
    
    def __init__(self):
        from app.core.config import settings
        self.mock_mode = settings.MOCK_MODE
        super().__init__(
            api_url=settings.CLOVA_EMBEDDING_URL,
            api_key=settings.CLOVA_EMBEDDING_API_KEY
        )
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding from text hash"""
        # Use hash to generate consistent embeddings for same text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # Convert hash to 1024-dim vector (Clova embedding size)
        embedding = []
        for i in range(0, 128):  # 128 * 8 = 1024
            chunk = text_hash[i % 32:(i % 32) + 1]
            val = int(chunk, 16) / 15.0 - 0.5  # Normalize to [-0.5, 0.5]
            embedding.extend([val] * 8)
        return embedding[:1024]
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self.mock_mode:
            logger.info(f"MOCK_MODE: Generating mock embedding for text (length: {len(text)})")
            return self._generate_mock_embedding(text)
        
        payload = {"text": text}
        result = await self._make_request("POST", "", json=payload)
        return result["result"]["embedding"]
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings


# Singleton instance
embedding_service = EmbeddingService()
