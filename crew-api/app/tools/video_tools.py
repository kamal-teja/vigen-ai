import os
import json
from typing import Dict, Tuple
from .bedrock_clients import (
    reel_start_async,
    reel_wait_for_completion,
    s3,http_url
)

REEL_DIMENSION = os.getenv("REEL_DIMENSION", "1280x720")  # TEXT_VIDEO requires 1280x720
REEL_FPS = int(os.getenv("REEL_FPS", "24"))
VIDEO_MODEL_ID = os.getenv("BEDROCK_VIDEO_MODEL_ID", "amazon.nova-reel-v1:1")

def _scene_prompt(scene: Dict) -> str:
    # Build a concise prompt from scene fields
    title = scene.get("title", "")
    vis = scene.get("visual_description", "")
    mood = scene.get("mood", "")
    style = scene.get("visual_style", "")
    hook = scene.get("hook", "")
    # Keep it short—Nova Reel TEXT_VIDEO is 6s per scene in your pipeline
    return (
        f"6-second shot. {title}. {hook}. Visuals: {vis}. Mood: {mood}. Style: {style}. "
        "Cinematic, crisp composition."
    ).strip()

def _parse_s3_uri(uri: str) -> Tuple[str, str]:
    """
    Returns (bucket, prefix) for an s3:// URI. If no prefix, returns ''.
    """
    if not uri.startswith("s3://"):
        raise ValueError(f"Expected s3:// URI, got: {uri}")
    rest = uri[5:]
    if "/" in rest:
        b, p = rest.split("/", 1)
        return b, p
    return rest, ""

# def generate_scene_video_from_image(bucket: str, img_key: str, scene: Dict, out_prefix: str) -> str:
#     """
#     Start a Nova Reel TEXT_VIDEO job (6s) and copy its output.mp4 to:
#       s3://{bucket}/{out_prefix}/scene_{scene_id}.mp4

#     We **must** pass only s3://{bucket} as the async output target. After completion,
#     Bedrock places output.mp4 under the prefix it reports back; we then copy it
#     into our run folder.
#     """
#     # Build model input for 6s TEXT_VIDEO
#     prompt = _scene_prompt(scene)
#     model_input = {
#         "taskType": "TEXT_VIDEO",
#         "textToVideoParams": {"text": prompt},
#         "videoGenerationConfig": {
#             "fps": REEL_FPS,
#             "durationSeconds": 6,              # TEXT_VIDEO fixed to 6s
#             "dimension": REEL_DIMENSION,       # <-- must be "1280x720"
#             "seed": 42,
#         },
#     }
#     base_s3_uri = f"s3://{bucket}"
#     arn = reel_start_async(VIDEO_MODEL_ID, model_input, base_s3_uri)
#     res = reel_wait_for_completion(arn, poll_secs=10, max_wait_secs=1800)
#     status = res.get("status")
#     if status != "Completed":
#         raise RuntimeError(f"Nova Reel job failed. Status={status}, details={json.dumps(res)}")

#     # Bedrock tells us which prefix it used
#     out_cfg = res.get("outputDataConfig", {}).get("s3OutputDataConfig", {})
#     job_s3_uri = out_cfg.get("s3Uri", base_s3_uri)  # e.g., s3://bucket or s3://bucket/some/prefix
#     src_bucket, src_prefix = _parse_s3_uri(job_s3_uri)

#     # The generated artifact is always named 'output.mp4' under that prefix
#     src_key = f"{src_prefix}/output.mp4" if src_prefix else "output.mp4"

#     # Our destination per scene
#     scene_id = scene.get("id", "1")
#     dest_key = f"{out_prefix}/scene_{scene_id}.mp4"

#     # Copy into our run folder
#     s3().copy_object(
#         Bucket=bucket,
#         Key=dest_key,
#         CopySource={"Bucket": src_bucket, "Key": src_key},
#     )

#     return dest_key



def generate_scene_video_from_image(bucket: str, img_key: str, scene: Dict, out_prefix: str) -> str:
    """
    Start a Nova Reel TEXT_VIDEO job (6s) and copy its output.mp4 to:
      s3://{bucket}/{out_prefix}/scene_{scene_id}.mp4

    Returns the exact destination key (relative path inside the bucket).
    """
    # Build model input for 6s TEXT_VIDEO
    prompt = _scene_prompt(scene)
    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {"text": prompt},
        "videoGenerationConfig": {
            "fps": REEL_FPS,
            "durationSeconds": 6,              # TEXT_VIDEO fixed to 6s
            "dimension": REEL_DIMENSION,       # <-- must be "1280x720"
            "seed": 42,
        },
    }

    base_s3_uri = f"s3://{bucket}"
    arn = reel_start_async(VIDEO_MODEL_ID, model_input, base_s3_uri)
    res = reel_wait_for_completion(arn, poll_secs=10, max_wait_secs=1800)
    status = res.get("status")

    if status != "Completed":
        raise RuntimeError(f"Nova Reel job failed. Status={status}, details={json.dumps(res)}")

    # Bedrock tells us which prefix it used
    out_cfg = res.get("outputDataConfig", {}).get("s3OutputDataConfig", {})
    job_s3_uri = out_cfg.get("s3Uri", base_s3_uri)  # e.g., s3://bucket/prefix
    src_bucket, src_prefix = _parse_s3_uri(job_s3_uri)

    # The generated artifact is always named 'output.mp4' under that prefix
    src_key = f"{src_prefix}/output.mp4" if src_prefix else "output.mp4"

    # Our destination per scene
    scene_id = scene.get("id", "1")
    dest_key = f"{out_prefix.rstrip('/')}/scene_{scene_id}.mp4"

    # Copy into our run folder (so it’s easy to locate)
    s3().copy_object(
        Bucket=bucket,
        Key=dest_key,
        CopySource={"Bucket": src_bucket, "Key": src_key},
    )

    print(f"[Nova Reel] Scene {scene_id} video saved to s3://{bucket}/{dest_key}")

    # ✅ Always return exact final S3 key (usable for presigned URL)
    return dest_key
