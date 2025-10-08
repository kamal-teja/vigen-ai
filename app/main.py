import os
import argparse
import json
from dotenv import load_dotenv

def parse_args():
    p = argparse.ArgumentParser(
        description="Agentic Ads Pipeline — choose video backend via CLI (everything else from .env)"
    )
    p.add_argument("--name", required=True, help="Product name")
    p.add_argument("--desc", required=True, help="Product description")
    p.add_argument("--idea", required=False, help="Advertisement idea (optional)")
    
    return p.parse_args()

def normalize_provider(val: str) -> str:
    v = (val or '').lower().strip()
    if v in ("kling",):
        return "kling"
    return "nova"

if __name__ == "__main__":
    args = parse_args()

    # Load .env BEFORE any imports that might read env variables
    load_dotenv()

    # os.environ["VIDEO_PROVIDER"] = normalize_provider(args.video_provider)

    from app.crew import run  # import AFTER .env is loaded

    result = run(args.name, args.desc, args.idea)
    print(json.dumps(result, indent=2))
