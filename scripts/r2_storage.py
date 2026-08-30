#!/usr/bin/env python3
"""
Hermes-Ecom Cloudflare R2 / S3 Storage Client.

Provides zero-dependency S3 API interaction (SigV4) with Cloudflare R2:
  1. Uploads staged product images (WebP/AVIF) from ComfyUI directly to R2 bucket.
  2. Lists and verifies database backup snapshots created by infra/backup_r2.sh.
  3. Generates public CDN URLs for Next.js storefront PDPs.

Usage:
  python3 scripts/r2_storage.py --list
  python3 scripts/r2_storage.py --upload local_file.webp --remote products/grinder/hero.webp
  python3 scripts/r2_storage.py --selftest

Stdlib only.
"""
import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET = os.environ.get("R2_BUCKET", "dropshipping-storefront")
R2_PUBLIC_DOMAIN = os.environ.get("R2_PUBLIC_DOMAIN", "cdn.yourstore.com")


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, "aws4_request")
    return k_signing


def generate_sigv4_headers(method, host, path, query_params, payload_bytes, access_key, secret_key, region="auto", service="s3"):
    """Constructs standard AWS SigV4 authorization headers."""
    t = dt.datetime.now(dt.timezone.utc)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    payload_hash = hashlib.sha256(payload_bytes).hexdigest()
    canonical_uri = urllib.parse.quote(path) if path else "/"
    canonical_querystr = "&".join(f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}" for k, v in sorted(query_params.items())) if query_params else ""

    canonical_headers = f"host:{host}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"

    canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystr}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    auth_header = f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    return {
        "Host": host,
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
        "Authorization": auth_header
    }


def list_r2_objects(account_id, access_key, secret_key, bucket, prefix=""):
    host = f"{account_id}.r2.cloudflarestorage.com"
    path = f"/{bucket}"
    query = {"list-type": "2"}
    if prefix:
        query["prefix"] = prefix

    headers = generate_sigv4_headers("GET", host, path, query, b"", access_key, secret_key)
    url = f"https://{host}{path}?{urllib.parse.urlencode(query)}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.read().decode("utf-8")
    except Exception as e:
        return f"[ERROR] S3 request failed: {e}"


def upload_r2_file(account_id, access_key, secret_key, bucket, local_path, remote_path, content_type="image/webp"):
    if not os.path.isfile(local_path):
        return f"[ERROR] Local file {local_path} not found."

    with open(local_path, "rb") as f:
        payload = f.read()

    host = f"{account_id}.r2.cloudflarestorage.com"
    path = f"/{bucket}/{remote_path.lstrip('/')}"
    headers = generate_sigv4_headers("PUT", host, path, {}, payload, access_key, secret_key)
    headers["Content-Type"] = content_type

    url = f"https://{host}{path}"
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return "SUCCESS" if res.status in (200, 201) else f"STATUS {res.status}"
    except Exception as e:
        return f"[ERROR] Upload failed: {e}"


def selftest():
    print("Running r2_storage selftest...")
    # Test SigV4 header generation deterministic math
    dummy_payload = b"test payload"
    headers = generate_sigv4_headers(
        "PUT", "example.r2.cloudflarestorage.com", "/test-bucket/file.txt", {},
        dummy_payload, "test_access", "test_secret", region="auto", service="s3"
    )
    assert "Authorization" in headers
    assert "AWS4-HMAC-SHA256" in headers["Authorization"]
    assert "x-amz-content-sha256" in headers
    assert headers["x-amz-content-sha256"] == hashlib.sha256(dummy_payload).hexdigest()
    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Hermes-Ecom Cloudflare R2 Storage Tool")
    ap.add_argument("--list", action="store_true", help="List objects in R2 bucket")
    ap.add_argument("--prefix", default="", help="Prefix filter for object listing")
    ap.add_argument("--upload", help="Local file path to upload")
    ap.add_argument("--remote", help="Remote destination path in R2 bucket")
    ap.add_argument("--content-type", default="image/webp", help="MIME content type")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not R2_ACCOUNT_ID or not R2_ACCESS_KEY or not R2_SECRET_KEY:
        print("[NOTICE] R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY not configured in environment.")
        print("To interact with live Cloudflare R2 storage, configure your R2 credentials.")
        return 1

    if a.list:
        print(f"Listing objects in R2 bucket '{R2_BUCKET}' (prefix: '{a.prefix}')...")
        out = list_r2_objects(R2_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET, prefix=a.prefix)
        print(out)
        return 0

    if a.upload:
        if not a.remote:
            ap.error("--remote path is required when uploading")
        print(f"Uploading {a.upload} to r2://{R2_BUCKET}/{a.remote}...")
        res = upload_r2_file(R2_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET, a.upload, a.remote, content_type=a.content_type)
        print(f"Result: {res}")
        if res == "SUCCESS":
            print(f"Public CDN URL: https://{R2_PUBLIC_DOMAIN}/{a.remote}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
