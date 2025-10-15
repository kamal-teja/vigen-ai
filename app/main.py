# import os
# import argparse
# import json
# from dotenv import load_dotenv

# def parse_args():
#     p = argparse.ArgumentParser(
#         description="Agentic Ads Pipeline — choose video backend via CLI (everything else from .env)"
#     )
#     p.add_argument("--name", required=True, help="Product name")
#     p.add_argument("--desc", required=True, help="Product description")
#     p.add_argument("--idea", required=False, help="Advertisement idea (optional)")
    
#     return p.parse_args()

# def normalize_provider(val: str) -> str:
#     v = (val or '').lower().strip()
#     if v in ("kling",):
#         return "kling"
#     return "nova"

# if __name__ == "__main__":
#     args = parse_args()

#     # Load .env BEFORE any imports that might read env variables
#     load_dotenv()

#     # os.environ["VIDEO_PROVIDER"] = normalize_provider(args.video_provider)

#     from app.crew import run  # import AFTER .env is loaded

#     result = run(args.name, args.desc, args.idea)
#     print(json.dumps(result, indent=2))



# import argparse, os
# from dotenv import load_dotenv
# load_dotenv()

# from app.crew import run  # import AFTER .env is loaded
# class Crewai():
#     def handel():
#         result = run(
#         args.name,
#         args.desc,
#         ad_idea=None,
#         video_length_seconds=args.video_length,   # ← pass through
#         product_image=args.product_image,         # ← pass through
#     )
#         print(result)
#         return result

# if __name__ == "__main__":
#     p = argparse.ArgumentParser()
#     p.add_argument("--name", required=True, help="Product name")
#     p.add_argument("--desc", required=True, help="Product description")
#     # NEW flags:
#     p.add_argument("--video-length", type=int, default=18, help="Total video length in seconds")
#     p.add_argument("--product-image", type=str, default=None,
#                    help="Optional path or S3 URL to a reference product image")
#     args = p.parse_args()

#     video_gen=Crewai()
#     video_gen.handel()


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.crew import run  # keep full import since app is the package

# Load environment variables
load_dotenv()

app = FastAPI(title="CrewAI Video Generator API")

@app.post("/generate-ad")
async def generate_ad(request: Request):
    """
    Generate an ad video given product details in JSON format.
    Expected JSON:
    {
        "name": "Smart Door Lock",
        "desc": "Secure, keyless home access with fingerprint unlock."
    }
    """
    try:
        data = await request.json()
        name = data.get("name")
        desc = data.get("desc")

        if not name or not desc:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "detail": "Both 'name' and 'desc' are required."}
            )

        # Run your CrewAI logic
        result = run(
            name,
            desc,
            ad_idea=None,
            video_length_seconds=None,
            product_image=None
        )

        return JSONResponse(content={
            "status": "success",
            "input": {"name": name, "desc": desc},
            "result": result
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


@app.get("/")
def root():
    return {"message": "CrewAI Ad Video Generator API is running 🚀"}

