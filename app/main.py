import os
from dotenv import load_dotenv
from fastapi import FastAPI, Body, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional
# Assuming these are in a sibling `app` directory
from app.dynamo_status import get_status
from app.crew import run

# Load environment variables from a .env file
load_dotenv()

# --- API Metadata ---
description = """
An API to generate marketing ad videos using a CrewAI-powered backend.
You can submit product details to kick off a generation process and check the status of the run.

**Key Features**:
- **Ad Generation**: Kick off an asynchronous workflow to generate a video.
- **Status Tracking**: Poll the status of the generation process using a unique `run_id`.
"""

app = FastAPI(
    title="CrewAI Video Generator API",
    description=description,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# --- Pydantic Models for Data Validation and Schema ---

class GenerateAdRequest(BaseModel):
    """Defines the JSON body for the ad generation request."""
    name: str = Field(..., example="Smart Door Lock", description="The name of the product.")
    desc: str = Field(..., min_length=10, example="Secure, keyless home access with fingerprint unlock and remote mobile control.", description="A detailed description of the product.")

class GenerateAdResponse(BaseModel):
    """The success response for the ad generation endpoint."""
    status: str = Field("success", example="success")
    run_id: str = Field(..., example="9f04705a33e6", description="A unique identifier for this generation job.")
    final_video_path: str = Field(..., "https:outputs/313c5c054712/final%20video/final_video.mp4",description="The final generated video URL. Available only when editing_status is 'completed'.")


class StatusResponse(BaseModel):
    """The response model for the status check endpoint."""
    id: str = Field(..., example="9f04705a33e6")
    script_generation_status: str = Field(..., example="completed")
    script_evaluation_status: str = Field(..., example="completed")
    video_generation_status: str = Field(..., example="running")
    audio_generation_status: str = Field(..., example="pending")
    editing_status: str = Field(..., example="pending")
    updated_at: str = Field(..., example="2025-10-17T02:01:18.123Z")
    final_video_uri: Optional[str] = Field(..., example="https:outputs/313c5c054712/final%20video/final_video.mp4", description="The final generated video URL. Available only when editing_status is 'completed'.")


class ErrorResponse(BaseModel):
    """A generic error response model."""
    detail: str = Field(..., example="A specific error message.")


# --- API Endpoints ---

@app.post(
    "/generate-ad",
    tags=["Ad Generation"],
    summary="Kick off a new ad video generation task",
    response_model=GenerateAdResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input provided."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    }
)
def generate_ad(payload: GenerateAdRequest = Body(...)):
    """
    Accepts product details and starts an asynchronous CrewAI workflow to generate a video.

    This endpoint immediately returns a `run_id` which can be used to track the
    progress of the video generation via the `/runs/{run_id}/status` endpoint.
    """
    try:
        # The `run` function returns a dictionary of results.
        crew_result = run(
            product_name=payload.name,
            product_desc=payload.desc
        )

        # --- FIX ---
        # Extract the actual run_id string from the result dictionary.
        run_id = crew_result.get("run_id")
        if not run_id or not isinstance(run_id, str):
            raise ValueError("The 'run' function did not return a valid 'run_id' string.")
        final_video=crew_result.get("final_video_uri")

        return {"status": "success", "run_id": run_id,"final_video_path":final_video}

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        # Catch other potential errors from the `run` function
        raise HTTPException(status_code=500, detail=f"Failed to start the crew run: {e}")


@app.get(
    "/runs/{run_id}/status",
    tags=["Status Tracking"],
    summary="Get the status of a generation run",
    response_model=StatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Run ID not found."},
    }
)
def get_run_status(run_id: str = Path(..., example="9f04705a33e6", description="The unique ID of the generation run.")):
    """
    Fetches the consolidated status of all steps in the video generation pipeline
    for a given `run_id`.
    """
    try:
        item = get_status(run_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Run with ID '{run_id}' not found.")
        return item
    except Exception as e:
        # This could happen if DynamoDB is unavailable or there's a permission issue
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching status: {e}")


@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint for health check",
    include_in_schema=False  # Hide this from the main docs
)
def root():
    """A simple health check endpoint to confirm the API is running."""
    return {"message": "CrewAI Ad Video Generator API is running 🚀"}

