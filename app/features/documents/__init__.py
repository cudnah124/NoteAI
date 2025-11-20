"""
Documents feature module
"""
from .router import router
from .service import DocumentService
from .processor import DocumentProcessor

__all__ = ["router", "DocumentService", "DocumentProcessor"]
