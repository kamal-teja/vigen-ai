from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    CREATOR = "creator"
    ADMIN = "admin"


class User(BaseModel):
    email: str  # Partition key
    full_name: str
    role: UserRole = UserRole.CREATOR
    password_hash: str
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str


class UserResponse(BaseModel):
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str
