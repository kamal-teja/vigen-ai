from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.adv import AdvStatus


class AdvertisementCreate(BaseModel):
    name: str
    desc: str = Field(min_length=10, description="Product description must be at least 10 characters long")


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


class AdvertisementStatusResponse(BaseModel):
    run_id: str
    status: AdvStatus
    crew_status: Optional[dict]  # Full crew API status object


class VideoUrlResponse(BaseModel):
    video_url: str


class AdvertisementUpdate(BaseModel):
    status: Optional[AdvStatus] = None
    final_video_uri: Optional[str] = None
