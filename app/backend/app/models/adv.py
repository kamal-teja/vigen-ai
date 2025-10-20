from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import enum


class AdvStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class Advertisement(BaseModel):
    user_id: str  # Partition key
    run_id: str  # Sort key and primary identifier
    name: str
    desc: str
    status: AdvStatus = AdvStatus.DRAFT
    final_video_uri: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdvertisementCreate(BaseModel):
    name: str
    desc: str


class AdvertisementResponse(BaseModel):
    run_id: str
    name: str
    desc: str
    status: AdvStatus
    final_video_uri: Optional[str]
    created_at: datetime
    updated_at: datetime


class AdvertisementCreateResponse(BaseModel):
    run_id: str
    status: AdvStatus
