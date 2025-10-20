# app/tools/image_tools.py
import os, json, base64, random
from tenacity import retry, stop_after_attempt, wait_exponential
from .bedrock_clients import bedrock_runtime, put_bytes_s3

def _get_image_model():
    mid = os.getenv("BEDROCK_IMAGE_MODEL_ID")
    if not mid:
        raise RuntimeError("BEDROCK_IMAGE_MODEL_ID (Nova Canvas) is required.")
    return mid

def _scene_prompt(scene: dict) -> str:
    vis = scene.get("visual_description", "")
    cam = scene.get("camera_directions", "")
    return (vis + (f" Camera: {cam}" if cam else "")).strip()

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def generate_scene_image(scene: dict, bucket: str, out_prefix: str) -> str:
    """
    out_prefix example: outputs/<RUN_ID>/scene image
    writes: outputs/<RUN_ID>/scene image/scene_<id>.png
    """
    model_id = _get_image_model()
    rt = bedrock_runtime()

    seed = random.randint(0, 858993460)
    native = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": _scene_prompt(scene)},
        "imageGenerationConfig": {
            "seed": seed,
            "quality": "standard",
            "height": 720,
            "width": 1280,
            "numberOfImages": 1,
        },
    }
    resp = rt.invoke_model(modelId=model_id, body=json.dumps(native))
    out = json.loads(resp["body"].read())
    img = base64.b64decode(out["images"][0])

    key = f"{out_prefix}/scene_{scene['id']}.png"
    put_bytes_s3(bucket, key, img, content_type="image/png")
    return key
