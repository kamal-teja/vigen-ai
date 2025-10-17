import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Body, HTTPException, Path, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional

from app.dynamo_status import get_status
from app.crew import run

load_dotenv()

description = """
An API to generate marketing ad videos using a CrewAI-powered backend.
Submit product details to kick off an asynchronous generation process and poll the status endpoint.
"""

app = FastAPI(
    title="CrewAI Video Generator API",
    description=description,
    version="1.1.0",
    contact={"name": "API Support", "email": "support@example.com"},
)

# --- Pydantic Models ---

class GenerateAdRequest(BaseModel):
    """Defines the JSON body for the ad generation request."""
    name: str = Field(description="The name of the product.", example="Smart Door Lock")
    desc: str = Field(
        min_length=10,
        description="A detailed description of the product.",
        example="Secure, keyless home access with fingerprint unlock."
    )
    run_id: str = Field(description="A unique identifier for this generation job.", example="sample-run-id-12345")


class GenerateAdResponse(BaseModel):
    """The success response for the ad generation endpoint."""
    status: str = Field(default="success", example="success")
    # MODIFICATION: Updated example to be more user-friendly.
    run_id: str = Field(description="A unique identifier for this generation job.", example="sample-run-id-12345")

class StatusResponse(BaseModel):
    """The response model for the status check endpoint."""
    # MODIFICATION: Updated example to be consistent.
    id: str = Field(example="sample-run-id-12345")
    script_generation_status: str = Field(example="completed")
    script_evaluation_status: str = Field(example="completed")
    video_generation_status: str = Field(example="running")
    audio_generation_status: str = Field(example="pending")
    editing_status: str = Field(example="pending")
    updated_at: str = Field(example="2025-10-17T02:01:18.123Z")
    final_video_uri: Optional[str] = Field(
        default=None,
        description="The final generated video URL. Will be populated once editing_status is 'completed'.",
        # MODIFICATION: Updated example to be consistent.
        example="https://vi-gen-dev.s3.amazonaws.com/outputs/sample-run-id-12345/final_video.mp4"
    )

class ErrorResponse(BaseModel):
    detail: str = Field(example="A specific error message.")

# --- API Endpoints ---

@app.post(
    "/generate-ad",
    tags=["Ad Generation"],
    summary="Kick off an asynchronous ad video generation task",
    response_model=GenerateAdResponse,
)
def generate_ad(payload: GenerateAdRequest, background_tasks: BackgroundTasks):
    """
    Accepts product details and starts an asynchronous workflow.
    This endpoint returns a `run_id` immediately, which is used to poll the status.
    """
    try:
        # Generate a unique ID for this run
        crew_result = run(
            product_name=payload.name,
            product_desc=payload.desc,
            current_run_id=payload.run_id
        )

        # --- FIX ---
        # Extract the actual run_id string from the result dictionary.
        run_id = crew_result.get("run_id")
        if not run_id or not isinstance(run_id, str):
            raise ValueError("The 'run' function did not return a valid 'run_id' string.")
        final_video=crew_result.get("final_video_uri")

        return {"status": "success", "run_id": run_id,"final_video_path":final_video}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start the background task: {e}")

@app.get(
    "/runs/{run_id}/status",
    tags=["Status Tracking"],
    summary="Get the status of a generation run",
    response_model=StatusResponse,
)
# MODIFICATION: Updated example to be consistent.
def get_run_status(run_id: str = Path(..., example="sample-run-id-12345")):
    """
    Fetches the consolidated status. Poll this endpoint until `editing_status`
    is 'completed' and `final_video_uri` is populated.
    """
    try:
        item = get_status(run_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Run with ID '{run_id}' not found.")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching status: {e}")

@app.get("/", tags=["General"], include_in_schema=False)
def root():
    return {"message": "CrewAI Ad Video Generator API is running 🚀"}

