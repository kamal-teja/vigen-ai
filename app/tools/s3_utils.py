# app/tools/s3_utils.py
import re
from urllib.parse import urlparse

def normalize_bucket_and_prefix(bucket_value: str | None, prefix_value: str | None = ""):
    """
    Accepts any of:
      - "vi-gen-dev"
      - "s3://vi-gen-dev"
      - "s3://vi-gen-dev/outputs"
      - "https://vi-gen-dev.s3.us-east-1.amazonaws.com/outputs"
      - "https://s3.us-east-1.amazonaws.com/vi-gen-dev/outputs" (path-style)
    Returns: (bucket_name, prefix_without_leading_slash)
    """
    s = (bucket_value or "").strip()
    p = (prefix_value or "").strip().lstrip("/")

    # s3:// form
    if s.startswith("s3://"):
        u = urlparse(s)
        bucket = u.netloc
        base_prefix = u.path.lstrip("/")
        prefix = "/".join(x for x in [base_prefix.rstrip("/"), p] if x)
        return bucket, prefix

    # https:// form (virtual-hosted or path-style)
    if s.startswith("http://") or s.startswith("https://"):
        u = urlparse(s)
        host = u.netloc
        path = u.path.lstrip("/")

        # virtual hosted: <bucket>.s3.<region>.amazonaws.com
        m = re.match(r"^([a-z0-9.-]+)\.s3[.-][a-z0-9-]+\.amazonaws\.com$", host)
        if m:
            bucket = m.group(1)
            base_prefix = path
            prefix = "/".join(x for x in [base_prefix.rstrip("/"), p] if x)
            return bucket, prefix

        # path-style: s3.<region>.amazonaws.com/<bucket>/...
        m2 = re.match(r"^s3[.-][a-z0-9-]+\.amazonaws\.com$", host)
        if m2 and path:
            parts = path.split("/", 1)
            bucket = parts[0]
            base_prefix = parts[1] if len(parts) > 1 else ""
            prefix = "/".join(x for x in [base_prefix.rstrip("/"), p] if x)
            return bucket, prefix

        # Fallback (unknown host form): return as-is with given prefix
        return s, p

    # Plain bucket name
    return s, p
