import json, os,re
from tenacity import retry, stop_after_attempt, wait_exponential
from .bedrock_clients import bedrock_runtime, put_json_s3


def _get_model_id():
    mid = os.getenv("BEDROCK_SCRIPT_MODEL_ID")
    if not mid:
        raise RuntimeError("BEDROCK_SCRIPT_MODEL_ID (Claude 3.7) is required.")
    return mid

def _unwrap_code_fence(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text or "", flags=re.S|re.I)
    return m.group(1) if m else (text or "")

def _extract_json_block(text: str) -> str:
    if not text: return ""
    start = text.find("{")
    if start == -1: return ""
    depth = 0
    for i,ch in enumerate(text[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return text[start:i+1]
    return ""

def _try_parse_json(raw: str):
    for candidate in [raw, _unwrap_code_fence(raw), _extract_json_block(raw)]:
        if not candidate: continue
        try:
            return json.loads(candidate)
        except Exception:
            continue
    raise ValueError("Model did not return valid JSON after cleanup attempts.")

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def generate_script(product_name: str, product_description: str, idea: str, prompt_template: str) -> dict:
    model_id = _get_model_id()
    rt = bedrock_runtime()

    prompt = (prompt_template
              .replace("{product_name}", (product_name or "").strip())
              .replace("{product_description}", (product_description or "").strip())
              .replace("{advertisement_idea}", (idea or "").strip()))

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0.5,
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }],
    }
    resp = rt.invoke_model(modelId=model_id, body=json.dumps(body))
    out = json.loads(resp["body"].read())
    text = out["content"][0]["text"]
    data = _try_parse_json(text)

    # Minimal shape checks & defaults
    scenes = data.get("scenes", [])
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("Script JSON missing 'scenes' list.")
    for i,sc in enumerate(scenes, 1):
        sc.setdefault("id", i)
        sc.setdefault("duration_seconds", 6)
        sc.setdefault("visual_description", "")
        sc.setdefault("dialogue", "")
        sc.setdefault("camera_directions", "")
        sc.setdefault("sfx", "")
        sc.setdefault("music_cue", "")
    return data

def save_script_s3(script, bucket, key):
     put_json_s3(bucket, key, script)
     return key