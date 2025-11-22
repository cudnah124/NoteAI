"""
Configuration module for NoteAI backend
Centralizes all environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ==============================================
    # Database Configuration
    # ==============================================
    DATABASE_URL: str = "postgresql://noteai_user:noteai_password@localhost:5432/noteai_db"
    TEST_DATABASE_URL: Optional[str] = None
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "noteai_user"
    DB_PASSWORD: str = "noteai_password"
    DB_NAME: str = "noteai_db"
    
    # ==============================================
    # Redis Configuration (Optional)
    # ==============================================
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # ==============================================
    # Security & Authentication
    # ==============================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==============================================
    # Development & Testing
    # ==============================================
    MOCK_MODE: bool = False  # Enable mock responses for development/testing
    
    # ==============================================
    # Naver Cloud Platform API Keys
    # ==============================================
    NAVER_API_KEY: str
    NAVER_API_SECRET: str
    NAVER_APIGW_KEY: str
    
    # ==============================================
    # HyperCLOVA X Configuration (LLM)
    # ==============================================
    HYPERCLOVA_API_KEY: str
    HYPERCLOVA_API_URL: str
    HYPERCLOVA_MODEL: str = "HCX-003"
    HYPERCLOVA_MAX_TOKENS: int = 2048
    HYPERCLOVA_TEMPERATURE: float = 0.7
    HYPERCLOVA_TOP_K: int = 50
    HYPERCLOVA_TOP_P: float = 0.8
    HYPERCLOVA_REPEAT_PENALTY: float = 1.2
    
    # ==============================================
    # Clova Embedding Configuration
    # ==============================================
    CLOVA_EMBEDDING_URL: str
    CLOVA_EMBEDDING_API_KEY: str
    EMBEDDING_MODEL: str = "clir-emb-dolphin"
    EMBEDDING_DIMENSION: int = 1024
    
    # ==============================================
    # Clova Speech (NEST) - Optional
    # ==============================================
    CLOVA_SPEECH_INVOKE_URL: Optional[str] = None
    CLOVA_SPEECH_SECRET: Optional[str] = None
    
    # ==============================================
    # Clova OCR - Optional
    # ==============================================
    CLOVA_OCR_URL: Optional[str] = None
    CLOVA_OCR_SECRET: Optional[str] = None
    
    # ==============================================
    # Vector Database (Qdrant)
    # ==============================================
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "noteai_chunks"
    QDRANT_DISTANCE_METRIC: str = "cosine"
    QDRANT_VECTOR_SIZE: int = 1024
    
    # ==============================================
    # Celery Configuration
    # ==============================================
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "Asia/Seoul"
    
    # ==============================================
    # Application Configuration
    # ==============================================
    APP_NAME: str = "NoteAI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered note-taking and document analysis system"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # ==============================================
    # CORS Configuration
    # ==============================================
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"
    CORS_ALLOW_HEADERS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ==============================================
    # Document Processing Configuration
    # ==============================================
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: str = "pdf,txt,docx,md,jpg,png"
    
    # Text Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 100
    
    # PDF Processing
    PDF_MAX_PAGES: int = 1000
    PDF_DPI: int = 300
    
    # ==============================================
    # RAG Configuration
    # ==============================================
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_MAX_CONTEXT_LENGTH: int = 4000
    
    # ==============================================
    # Rate Limiting & Security
    # ==============================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    REQUEST_TIMEOUT: int = 30
    
    # ==============================================
    # Logging Configuration
    # ==============================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760
    LOG_BACKUP_COUNT: int = 5
    
    # ==============================================
    # Monitoring & Metrics
    # ==============================================
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    
    # ==============================================
    # Storage Configuration
    # ==============================================
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "uploads"
    
    # AWS S3 (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: str = "ap-northeast-2"
    
    # ==============================================
    # Email Configuration (Optional)
    # ==============================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@noteai.com"
    SMTP_USE_TLS: bool = True
    
    # ==============================================
    # Feature Flags
    # ==============================================
    ENABLE_REGISTRATION: bool = True
    ENABLE_EMAIL_VERIFICATION: bool = False
    ENABLE_FILE_UPLOAD: bool = True
    ENABLE_YOUTUBE_IMPORT: bool = True
    ENABLE_WEB_SCRAPING: bool = True
    ENABLE_OCR: bool = True
    ENABLE_SPEECH_TO_TEXT: bool = True
    
    # ==============================================
    # Development Settings
    # ==============================================
    RELOAD: bool = False
    DEBUG_SQL: bool = False
    ENABLE_API_DOCS: bool = True
    ENABLE_SWAGGER_UI: bool = True
    
    # ==============================================
    # Production Deployment
    # ==============================================
    WORKERS: int = 4
    WORKER_CLASS: str = "uvicorn.workers.UvicornWorker"
    KEEPALIVE: int = 5
    GRACEFUL_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()
