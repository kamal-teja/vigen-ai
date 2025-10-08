import os, json, time, uuid, requests
from typing import Optional
from .bedrock_clients import put_bytes_s3, http_url, presigned_http_url

PROVIDER = os.getenv("KLING_PROVIDER", "aimlapi").lower()  # aimlapi | piapi
BASE_URL = os.getenv("KLING_BASE_URL", "").rstrip("/")
API_KEY  = os.getenv("KLING_API_KEY", "")
MODEL    = os.getenv("KLING_MODEL", "kling-ai/v1.6-pro/image-to-video")
RES      = os.getenv("KLING_RESOLUTION", "1080p")
FPS      = int(os.getenv("KLING_FPS", "24"))
MAX_WAIT = int(os.getenv("KLING_MAX_WAIT_SECS", "900"))
POLL_INT = int(os.getenv("KLING_POLL_INTERVAL_SECS", "8"))

HEADERS  = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

class KlingJobError(RuntimeError): ...

def _image_http_url(bucket: str, key: str) -> str:
    # Prefer presigned for private buckets; fall back to public path if you’ve made it public.
    try:
        return presigned_http_url(bucket, key, expires_in=3600)
    except Exception:
        return f"https://{bucket}.s3.amazonaws.com/{key}"

# ---------- Provider shapes ----------

def _start_job_aimlapi(image_url: str, prompt: str, duration: int) -> str:
    """
    AIMLAPI typical pattern:
      POST {BASE_URL}/v1/jobs
      body = {"model": MODEL, "input": {...}}
      -> {"id": "...", "status":"queued"}
    Docs vary by model; adjust if your provider uses /generate endpoints. 
    """
    url = f"{BASE_URL}/v1/jobs"
    body = {
        "model": MODEL,
        "input": {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "resolution": RES,
            "fps": FPS
        }
    }
    r = requests.post(url, headers=HEADERS, data=json.dumps(body), timeout=60)
    if r.status_code >= 300:
        raise KlingJobError(f"AIMLAPI start failed: {r.status_code} {r.text}")
    job = r.json()
    return job.get("id") or job.get("job_id")

def _poll_job_aimlapi(job_id: str) -> Optional[str]:
    """Return final video URL or None if still running."""
    url = f"{BASE_URL}/v1/jobs/{job_id}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code >= 300:
        raise KlingJobError(f"AIMLAPI poll failed: {r.status_code} {r.text}")
    j = r.json()
    status = j.get("status")
    if status in ("queued", "processing", "running"):
        return None
    if status in ("succeeded", "completed"):
        # Common shapes: output.video_url OR output[0] OR result.url
        output = j.get("output") or {}
        if isinstance(output, dict):
            return output.get("video_url") or output.get("url")
        if isinstance(output, list) and output:
            return output[0] if isinstance(output[0], str) else output[0].get("url")
    raise KlingJobError(f"AIMLAPI job failed or unknown status: {j}")

def _start_job_piapi(image_url: str, prompt: str, duration: int) -> str:
    """
    PiAPI typical pattern (subject to change):
      POST {BASE_URL}/kling/jobs
      body = {"model": MODEL, "input": {...}}
      -> {"id":"..."}
    """
    url = f"{BASE_URL}/kling/jobs"
    body = {"model": MODEL, "input": {"image_url": image_url, "prompt": prompt, "duration": duration, "resolution": RES}}
    r = requests.post(url, headers=HEADERS, data=json.dumps(body), timeout=60)
    if r.status_code >= 300:
        raise KlingJobError(f"PiAPI start failed: {r.status_code} {r.text}")
    return r.json().get("id")

def _poll_job_piapi(job_id: str) -> Optional[str]:
    url = f"{BASE_URL}/kling/jobs/{job_id}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code >= 300:
        raise KlingJobError(f"PiAPI poll failed: {r.status_code} {r.text}")
    j = r.json()
    status = j.get("status")
    if status in ("queued", "processing", "running"):
        return None
    if status in ("succeeded", "completed"):
        out = j.get("output") or {}
        return out.get("video_url") or out.get("url")
    raise KlingJobError(f"PiAPI job failed or unknown status: {j}")

# ---------- Router ----------

def _start_job(image_url: str, prompt: str, duration: int) -> str:
    if PROVIDER == "piapi":
        return _start_job_piapi(image_url, prompt, duration)
    # default: aimlapi
    return _start_job_aimlapi(image_url, prompt, duration)

def _poll_job(job_id: str) -> Optional[str]:
    if PROVIDER == "piapi":
        return _poll_job_piapi(job_id)
    # default: aimlapi
    return _poll_job_aimlapi(job_id)

# ---------- Public API ----------

def build_kling_prompt(scene: dict) -> str:
    base = scene.get("visual_description", "")
    cam  = scene.get("camera_directions", "")
    return f"{base}. Subtle, cinematic motion. {('Camera: ' + cam) if cam else ''}".strip()

def generate_scene_video_kling(bucket: str, image_key: str, scene: dict, out_prefix: str) -> str:
    """
    Submit image→video job to Kling provider, poll until ready, then copy bytes to S3 (if the provider returns a URL).
    Returns S3 key of the stored MP4.
    """
    if not API_KEY or not BASE_URL:
        raise KlingJobError("KLING_API_KEY or KLING_BASE_URL not configured")

    img_url = _image_http_url(bucket, image_key)
    prompt  = build_kling_prompt(scene)
    duration = max(3, min(12, int(scene.get("duration_seconds", 6))))

    job_id = _start_job(img_url, prompt, duration)

    deadline = time.time() + MAX_WAIT
    video_url = None
    while time.time() < deadline:
        time.sleep(POLL_INT)
        video_url = _poll_job(job_id)
        if video_url:
            break

    if not video_url:
        raise KlingJobError(f"Kling job timed out after {MAX_WAIT}s (job_id={job_id})")

    # Download & push to your S3
    resp = requests.get(video_url, timeout=300)
    if resp.status_code >= 300:
        raise KlingJobError(f"Failed downloading Kling output: {resp.status_code}")
    key = f"{out_prefix}/video/scene_{scene['id']}_{uuid.uuid4().hex}.mp4"
    put_bytes_s3(bucket, key, resp.content, content_type="video/mp4")
    return key
