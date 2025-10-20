import json, os, re
from tenacity import retry, stop_after_attempt, wait_exponential
from .bedrock_clients import bedrock_runtime

def _get_model_id():
    return os.getenv("BEDROCK_IDEA_MODEL_ID") or os.getenv("BEDROCK_SCRIPT_MODEL_ID")

def _require(mid):
    if not mid:
        raise RuntimeError("Set BEDROCK_IDEA_MODEL_ID or BEDROCK_SCRIPT_MODEL_ID (Claude 3.7) in .env")

def _unwrap_code_fence(text: str) -> str:
    m = re.match(r"```(?:json)?\s*(.*?)\s*```", (text or "").strip(), flags=re.S|re.I)
    return m.group(1) if m else (text or "")

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def generate_ad_idea(product_name: str, product_description: str, prompt_template: str) -> str:
    model_id = _get_model_id(); _require(model_id)
    rt = bedrock_runtime()

    prompt = (prompt_template
              .replace("{{product_name}}", (product_name or "").strip())
              .replace("{{product_description}}", (product_description or "").strip()))

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }],
    }
    resp = rt.invoke_model(modelId=model_id, body=json.dumps(body))
    out = json.loads(resp["body"].read())
    text = out["content"][0]["text"]
    text = _unwrap_code_fence(text)
    try:
        data = json.loads(text)
        return data.get("idea") or text.strip()
    except Exception:
        return text.strip()
