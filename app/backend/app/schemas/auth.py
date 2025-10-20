from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: Optional[str] = "creator"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserResponse(BaseModel):
    email: str
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
