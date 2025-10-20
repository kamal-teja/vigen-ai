from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import timedelta
from app.database import dynamodb_service
from app.utils.rate_limiter import rate_limit
from app.schemas.auth import UserRegister, UserLogin, Token, RefreshTokenRequest, UserResponse
from app.models.user import User
from app.services.auth_service import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(max_requests=3, window_seconds=300)  # 3 registrations per 5 minutes
def register(user_data: UserRegister, request: Request):
    """Register a new user"""
    # Check if user already exists
    existing_user = dynamodb_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length for bcrypt (72 byte limit)
    pw_bytes = user_data.password.encode('utf-8') if isinstance(user_data.password, str) else user_data.password
    if len(pw_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long. Maximum 72 bytes allowed."
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = dynamodb_service.create_user({
        'email': user_data.email,
        'full_name': user_data.full_name,
        'role': user_data.role,
        'password_hash': hashed_password
    })
    
    return UserResponse(
        email=new_user['email'],
        full_name=new_user['full_name'],
        role=new_user['role'],
        created_at=new_user['created_at'],
        updated_at=new_user['updated_at']
    )


@router.post("/login", response_model=Token)
@rate_limit(max_requests=5, window_seconds=300)  # 5 login attempts per 5 minutes
def login(user_credentials: UserLogin, request: Request):
    """Login user and return JWT tokens (access + refresh)"""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@rate_limit(max_requests=20, window_seconds=60)  # 20 token refreshes per minute
def refresh_token(token_request: RefreshTokenRequest, request: Request):
    """Refresh access token using refresh token"""
    email = verify_refresh_token(token_request.refresh_token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user still exists
    user_data = dynamodb_service.get_user_by_email(email)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    refresh_token = create_refresh_token(data={"sub": email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
@rate_limit(max_requests=30, window_seconds=60)  # 30 user info requests per minute
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
