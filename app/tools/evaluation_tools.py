import json, os
from tenacity import retry, stop_after_attempt, wait_exponential
from .bedrock_clients import converse_text
from dotenv import load_dotenv
load_dotenv()

def _get_eval_model():
    mid = os.getenv("BEDROCK_EVAL_MODEL_ID")
    if not mid:
        raise RuntimeError("BEDROCK_EVAL_MODEL_ID (Nova Lite) is required.")
    return mid

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def evaluate_script(product_name: str, product_desc: str, script_dict: dict, rubric_markdown: str) -> dict:
    # print("We are in eval script===============")
    model_id = _get_eval_model()
    # print("eval modelid=========14===",model_id)
    # Build a single user message for Nova Lite Conversation API
    payload = (
        f"Rubric:\n{rubric_markdown}\n\n"
        f"Product Name: {product_name}\n"
        f"Product Description: {product_desc}\n\n"
        f"Advertisement Story and Script (JSON):\n{json.dumps(script_dict, ensure_ascii=False)}\n\n"
        "Return STRICT JSON only per rubric."
    )

    text = converse_text(model_id, payload, max_tokens=800, temperature=0.2, top_p=0.9)

    # Expect strict JSON per our rubric; still guard-parse
    try:
        return json.loads(text)
    except Exception as e:
        # Last resort: find first balanced JSON in text
        start = text.find("{"); end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise
