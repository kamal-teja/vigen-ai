import boto3, json, os
from botocore.config import Config
from botocore.exceptions import ClientError

_region = os.getenv("AWS_REGION", "us-east-1")
_cfg = Config(retries={"max_attempts": 10, "mode": "standard"})

# --------- S3 ----------
def s3():
    return boto3.client("s3", region_name=_region)

# --------- Bedrock Runtime ----------
def bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=_region)

# Convenience Bedrock runtime singleton for Nova Reel helpers
_rt = None
def rt():
    global _rt
    if _rt is None:
        _rt = boto3.client("bedrock-runtime", region_name=_region)
    return _rt

def presigned_http_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    """
    Generate a secure presigned HTTPS URL for accessing a private S3 object.

    Args:
        bucket (str): The S3 bucket name.
        key (str): The object key (path inside the bucket).
        expires_in (int): Expiration in seconds (default: 1 hour).

    Returns:
        str: A temporary, signed HTTPS URL for direct access.
    """
    try:
        s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        print(f"[S3] Generated presigned URL for {bucket}/{key}")
        return url

    except Exception as e:
        print(f"[S3 Error] Failed to create presigned URL for {bucket}/{key}: {e}")
        raise

# ---------- Nova Lite convenience (Conversation API) ----------
def converse_text(model_id: str, text: str, max_tokens=512, temperature=0.5, top_p=0.9):
    client = bedrock_runtime()
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": text}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature, "topP": top_p},
    )
    return resp["output"]["message"]["content"][0]["text"]

# ---------- Nova Reel async helpers ----------
def reel_start_async(model_id: str, model_input: dict, s3_uri: str) -> str:
    """
    Start a Nova Reel async invoke and return the invocationArn.
    Pass ONLY 's3://<bucket>' (no prefix). If a prefix is provided by mistake,
    we fall back to root bucket automatically.
    """
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Nova Reel output must be an s3:// URI. Got: {s3_uri}")

    # If a prefix was passed, strip it to satisfy service expectation.
    # (Some accounts accept a prefix; many return 'Invalid Output Config'.)
    bucket_only = "s3://" + s3_uri[5:].split("/", 1)[0]

    def _invoke(uri):
        return rt().start_async_invoke(
            modelId=model_id,
            modelInput=model_input,
            outputDataConfig={"s3OutputDataConfig": {"s3Uri": uri}},
        )

    try:
        try:
            return _invoke(bucket_only)["invocationArn"]
        except ClientError as e:
            # For visibility while debugging
            print(f"[Nova Reel] StartAsyncInvoke failed with bucket-only URI={bucket_only}: {e}")
            raise

    except ClientError as e:
        msg = str(e)
        if "Invalid Output Config" in msg or "Credentials" in msg:
            raise RuntimeError(
                "Nova Reel async invoke failed: Invalid Output Config/Credentials.\n"
                f"Attempted S3 URI: {bucket_only}\n"
                "Check that:\n"
                "  • outputDataConfig.s3OutputDataConfig.s3Uri == 's3://<bucket>' (NO https://, NO ARN, NO prefix)\n"
                "  • Your caller identity has s3:PutObject on that bucket\n"
                "  • Bucket is in the same region and bucket policy doesn’t require KMS-only writes"
            ) from e
        raise

def reel_get_status(invocation_arn: str) -> dict:
    return rt().get_async_invoke(invocationArn=invocation_arn)

def reel_wait(invocation_arn: str, poll_secs: int = 10, timeout_secs: int = 1800) -> dict:
    """
    Polls until status in ('Completed','Failed'). Returns the full get_async_invoke() payload.
    """
    import time
    start = time.time()
    last = None
    while True:
        out = reel_get_status(invocation_arn)
        st = out.get("status", "")
        if st != last:
            print(f"[Nova Reel] status: {st}")
            last = st
        if st in ("Completed", "Failed", "Stopped"):
            return out
        if time.time() - start > timeout_secs:
            raise TimeoutError(f"Nova Reel async job timed out after {timeout_secs}s")
        time.sleep(poll_secs)

# 🔧 Alias expected by other modules (e.g., video_tools.py)
def reel_wait_for_completion(invocation_arn: str, poll_secs: int = 8, max_wait_secs: int = 1800) -> dict:
    """Compatibility wrapper so imports like `reel_wait_for_completion` work."""
    return reel_wait(invocation_arn, poll_secs=poll_secs, timeout_secs=max_wait_secs)

# (Kept for compatibility if anything else calls it)
def reel_get_async(invocation_arn: str):
    client = bedrock_runtime()
    return client.get_async_invoke(invocationArn=invocation_arn)

# ---------- Misc AWS helpers ----------
def put_bytes_s3(bucket, key, data: bytes, content_type="application/octet-stream"):
    """Store raw bytes to S3 with no explicit SSE/KMS (bucket policy controls encryption)."""
    s3().put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
    return key

def put_json_s3(bucket, key, obj):
    """Store JSON to S3 with no explicit SSE/KMS (bucket policy controls encryption)."""
    s3().put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(obj, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )
    return key

def polly():
    return boto3.client("polly", region_name=_region, config=_cfg)

def mediaconvert():
    # endpoint can be discovered once and stored
    endpoint = os.getenv("MEDIACONVERT_ENDPOINT", "").strip()
    mc = boto3.client(
        "mediaconvert",
        region_name=_region,
        config=_cfg,
        endpoint_url=endpoint if endpoint else None,
    )
    if not endpoint:
        # discover and cache
        endpoints = mc.describe_endpoints()
        url = endpoints["Endpoints"][0]["Url"]
        os.environ["MEDIACONVERT_ENDPOINT"] = url
        mc = boto3.client("mediaconvert", region_name=_region, config=_cfg, endpoint_url=url)
    return mc

def presigned_http_url(bucket, key, expires_in=3600):
    return s3().generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )

def s3_url(bucket, key):
    return f"s3://{bucket}/{key.lstrip('/')}"

def http_url(bucket, key, region=_region):
    # If the bucket is public/static website or CloudFront in front, adjust here.
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key.lstrip('/')}"
