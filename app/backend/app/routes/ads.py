from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import requests
import uuid
import logging
from app.database import dynamodb_service
from app.models.user import User
from app.models.adv import AdvStatus
from app.utils.rate_limiter import rate_limit
from app.schemas.adv import (
    AdvertisementCreate,
    AdvertisementResponse,
    AdvertisementCreateResponse,
    AdvertisementStatusResponse,
    VideoUrlResponse,
    AdvertisementUpdate,
)
from app.services.auth_service import get_current_user
from app.services.s3_service import s3_service
from app.config import settings

router = APIRouter(prefix="/ads", tags=["Advertisements"])


def _get_user_advertisement_or_404(
    run_id: str,
    current_user: User
) -> dict:
    ad = dynamodb_service.get_advertisement(current_user.email, run_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertisement not found"
        )
    return ad


@router.post("", response_model=AdvertisementCreateResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(max_requests=5, window_seconds=60)  # 5 creates per minute
def create_advertisement(
    ad_data: AdvertisementCreate,
    current_user: User = Depends(get_current_user)
):
    run_id = str(uuid.uuid4())
    ad_item = dynamodb_service.create_advertisement(current_user.email, {
        'name': ad_data.name,
        'desc': ad_data.desc,
        'run_id': run_id,
        'status': AdvStatus.IN_PROGRESS.value
    })

    if not settings.CREW_ENDPOINT_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Crew endpoint not configured"
        )

    crew_payload = {
        "name": ad_data.name,
        "desc": ad_data.desc,
        "run_id": run_id
    }

    try:
        crew_response = requests.post(f"{settings.CREW_ENDPOINT_URL}/generate-ad", json=crew_payload, timeout=5)
        crew_response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Crew API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Crew API response status: {e.response.status_code}")
            logging.error(f"Crew API response text: {e.response.text}")
        logging.error(f"Payload sent: {crew_payload}")
        dynamodb_service.update_advertisement(current_user.email, ad_item['run_id'], {
            'status': AdvStatus.FAILED.value
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate ad generation: {str(e)}"
        )

    return AdvertisementCreateResponse(run_id=run_id, status=AdvStatus.IN_PROGRESS)


@router.get("/{run_id}/status", response_model=AdvertisementStatusResponse)
@rate_limit(max_requests=15, window_seconds=1)  # 15 requests per second for polling
def get_advertisement_status(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    ad = _get_user_advertisement_or_404(run_id, current_user)

    if not ad.get('run_id'):
        return AdvertisementStatusResponse(
            run_id=ad['run_id'],
            status=AdvStatus(ad['status']),
            crew_status=None
        )

    try:
        status_response = requests.get(f"{settings.CREW_ENDPOINT_URL}/runs/{ad['run_id']}/status", timeout=5)
        status_response.raise_for_status()
        status_data = status_response.json()

        new_status = AdvStatus.IN_PROGRESS

        failed_steps = [
            status_data.get("script_generation_status") == "FAILED",
            status_data.get("script_evaluation_status") == "FAILED",
            status_data.get("video_generation_status") == "FAILED",
            status_data.get("audio_generation_status") == "FAILED",
            status_data.get("editing_status") == "FAILED"
        ]

        if any(failed_steps):
            new_status = AdvStatus.FAILED
        else:
            steps_status = [
                status_data.get("script_generation_status") == "COMPLETED",
                status_data.get("script_evaluation_status") == "COMPLETED",
                status_data.get("video_generation_status") == "COMPLETED",
                status_data.get("audio_generation_status") == "COMPLETED",
                status_data.get("editing_status") == "COMPLETED",
                "final_video_uri" in status_data and status_data["final_video_uri"]
            ]

            if all(steps_status):
                new_status = AdvStatus.GENERATED
                if "final_video_uri" in status_data and not ad.get('final_video_uri'):
                    dynamodb_service.update_advertisement(current_user.email, run_id, {
                        'final_video_uri': status_data["final_video_uri"],
                        'status': new_status.value
                    })

        if new_status.value != ad['status']:
            updates = {'status': new_status.value}
            if new_status == AdvStatus.FAILED:
                updates['status_reason'] = "One or more generation steps failed"
            dynamodb_service.update_advertisement(current_user.email, run_id, updates)

        return AdvertisementStatusResponse(
            run_id=ad['run_id'],
            status=new_status,
            crew_status=status_data
        )

    except requests.RequestException:
        return AdvertisementStatusResponse(
            run_id=ad['run_id'],
            status=AdvStatus(ad['status']),
            crew_status=None
        )


@router.get("/{run_id}/video-url", response_model=VideoUrlResponse)
@rate_limit(max_requests=10, window_seconds=60)  # 10 video URL requests per minute
def get_video_presigned_url(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    ad = _get_user_advertisement_or_404(run_id, current_user)

    if not ad.get('final_video_uri'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Extract S3 object key from the full S3 URL
    # final_video_uri is expected to be in format: https://bucket-name.s3.amazonaws.com/path/to/video.mp4
    if ad['final_video_uri'].startswith("https://"):
        url_without_protocol = ad['final_video_uri'].replace("https://", "")
        domain_end = url_without_protocol.find('/')
        if domain_end != -1:
            key = url_without_protocol[domain_end + 1:]
        else:
            key = ""
    else:
        # Fallback: assume it's already just the key
        key = ad['final_video_uri']

    # Security: Validate S3 key format to prevent path traversal
    if not key or ".." in key or key.startswith("/") or not key.endswith(('.mp4', '.mov', '.avi', '.webm')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video file"
        )

    try:
        # Use shorter expiration for security (15 minutes instead of 1 hour)
        presigned_url = s3_service.generate_presigned_download_url(key, expiration=900)
        
        # Log presigned URL generation for audit trail
        logger = logging.getLogger(__name__)
        logger.info(f"Generated presigned URL for user {current_user.email}, ad {run_id}, key {key}")
        
        return VideoUrlResponse(video_url=presigned_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video URL: {str(e)}"
        )


@router.get("/{run_id}", response_model=AdvertisementResponse)
@rate_limit(max_requests=30, window_seconds=60)  # 30 gets per minute
def get_advertisement(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    ad = _get_user_advertisement_or_404(run_id, current_user)

    return AdvertisementResponse(
        run_id=ad['run_id'],
        name=ad['name'],
        desc=ad['desc'],
        status=AdvStatus(ad['status']),
        final_video_uri=ad.get('final_video_uri'),
        created_at=datetime.fromisoformat(ad['created_at']),
        updated_at=datetime.fromisoformat(ad['updated_at'])
    )


@router.put("/{run_id}", response_model=AdvertisementResponse)
@rate_limit(max_requests=10, window_seconds=60)  # 10 updates per minute
def update_advertisement(
    run_id: str,
    update_data: AdvertisementUpdate,
    current_user: User = Depends(get_current_user)
):
    ad = _get_user_advertisement_or_404(run_id, current_user)

    # Prepare updates dict
    updates = {}
    if update_data.status is not None:
        updates['status'] = update_data.status.value
    if update_data.final_video_uri is not None:
        updates['final_video_uri'] = update_data.final_video_uri

    if not updates:
        # No updates provided, return current ad
        return AdvertisementResponse(
            run_id=ad['run_id'],
            name=ad['name'],
            desc=ad['desc'],
            status=AdvStatus(ad['status']),
            final_video_uri=ad.get('final_video_uri'),
            created_at=datetime.fromisoformat(ad['created_at']),
            updated_at=datetime.fromisoformat(ad['updated_at'])
        )

    # Update the advertisement
    success = dynamodb_service.update_advertisement(current_user.email, run_id, updates)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update advertisement"
        )

    # Get updated advertisement
    updated_ad = dynamodb_service.get_advertisement(current_user.email, run_id)
    if not updated_ad:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated advertisement"
        )

    return AdvertisementResponse(
        run_id=updated_ad['run_id'],
        name=updated_ad['name'],
        desc=updated_ad['desc'],
        status=AdvStatus(updated_ad['status']),
        final_video_uri=updated_ad.get('final_video_uri'),
        created_at=datetime.fromisoformat(updated_ad['created_at']),
        updated_at=datetime.fromisoformat(updated_ad['updated_at'])
    )


@router.get("", response_model=List[AdvertisementResponse])
@rate_limit(max_requests=20, window_seconds=60)  # 20 list requests per minute
def get_user_advertisements(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if status:
        # Query by status using GSI
        ads = dynamodb_service.get_user_advertisements_by_status(current_user.email, status)
    else:
        # Get all user advertisements
        ads = dynamodb_service.get_user_advertisements(current_user.email)

    return [
        AdvertisementResponse(
            run_id=ad['run_id'],
            name=ad['name'],
            desc=ad['desc'],
            status=AdvStatus(ad['status']),
            final_video_uri=ad.get('final_video_uri'),
            created_at=datetime.fromisoformat(ad['created_at']),
            updated_at=datetime.fromisoformat(ad['updated_at'])
        )
        for ad in ads
    ]
