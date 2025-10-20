#!/usr/bin/env python3
import os, sys, re
from dotenv import load_dotenv
import boto3

def fail(msg, code=1):
    print(f"❌ {msg}"); sys.exit(code)

def ok(msg):
    print(f"✅ {msg}")

def warn(msg):
    print(f"⚠️  {msg}")

def main():
    load_dotenv()
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    bucket = os.getenv("S3_BUCKET", "")
    s3_prefix = os.getenv("S3_PREFIX", "outputs")
    script_id = os.getenv("BEDROCK_SCRIPT_MODEL_ID")
    eval_id = os.getenv("BEDROCK_EVAL_MODEL_ID")
    image_id = os.getenv("BEDROCK_IMAGE_MODEL_ID")
    video_id = os.getenv("BEDROCK_VIDEO_MODEL_ID")
    role_arn = os.getenv("MEDIACONVERT_ROLE_ARN")

    # 1) STS identity
    try:
        sts = boto3.client("sts", region_name=region)
        ident = sts.get_caller_identity()
        ok(f"STS identity ok: Account={ident.get('Account')} Arn={ident.get('Arn')}")
    except Exception as e:
        fail(f"AWS credentials not valid for STS: {e}")

    # 2) S3 bucket syntax + write test
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket or ""):
        fail(f"Invalid S3 bucket name: {bucket!r}")
    s3 = boto3.client("s3", region_name=region)
    key = f"{s3_prefix.strip('/')}/preflight/ping.txt"
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=b"ok", ContentType="text/plain")
        ok(f"S3 PUT ok: s3://{bucket}/{key}")
    except Exception as e:
        fail(f"S3 PUT failed to s3://{bucket}/{key}: {e}")

    # 3) Bedrock model visibility (control plane, no invoke)
    try:
        bedrock = boto3.client("bedrock", region_name=region)
        # Some SDKs don't paginate this; call once.
        resp = bedrock.list_foundation_models()
        models = [m.get("modelId") for m in resp.get("modelSummaries", [])]
        required = [("BEDROCK_SCRIPT_MODEL_ID", script_id),
                    ("BEDROCK_EVAL_MODEL_ID",   eval_id),
                    ("BEDROCK_IMAGE_MODEL_ID",  image_id),
                    ("BEDROCK_VIDEO_MODEL_ID",  video_id)]
        for name, mid in required:
            if not mid:
                fail(f"{name} is not set.")
            present = any(str(mid).strip() == m for m in models)
            if present:
                ok(f"Bedrock access ok for {name}={mid}")
            else:
                warn(f"{name}={mid} not listed by ListFoundationModels. This can be normal if the account/region hides some models or you lack permissions. If invokes fail, re-check model access in the Bedrock console.")
    except Exception as e:
        warn(f"Could not list Bedrock foundation models: {e}. If invokes fail, verify model access in the console.")

    # 4) MediaConvert endpoint discover
    try:
        mc = boto3.client("mediaconvert", region_name=region)
        ep = mc.describe_endpoints()["Endpoints"][0]["Url"]
        ok(f"MediaConvert endpoint discovered: {ep}")
        if role_arn:
            ok(f"MediaConvert role ARN set: {role_arn}")
        else:
            warn("MEDIACONVERT_ROLE_ARN not set. Mux jobs will fail without a role that can read/write your S3 bucket.")
    except Exception as e:
        warn(f"MediaConvert endpoint discovery failed: {e}")

    print("\nAll preflight checks completed. If everything is green, you're good to run the pipeline.")
    return 0

if __name__ == "__main__":
    sys.exit(main())