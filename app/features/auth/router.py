"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get auth service instance"""
    return AuthService(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    return await service.register_user(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate user and receive JWT access token"
)
async def login(
    user_data: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    """Login and get access token"""
    return await service.login_user(user_data)
