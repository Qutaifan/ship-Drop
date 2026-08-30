#!/usr/bin/env python3
"""
Temu Open Platform EU API Client & V3 Method Tester.
"""
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ENDPOINT_EU = "https://openapi-b-eu.temu.com/openapi/router"
ENDPOINT_GLOBAL = "https://openapi-b-global.temu.com/openapi/router"

def _require(name):
    """Credentials come from the environment only.

    These were previously hardcoded as fallback defaults — an app key, an app
    secret and a live access token sitting in plaintext in a file destined for a
    public repository. Never reintroduce a default here.
    """
    v = os.environ.get(name)
    if not v:
        raise SystemExit(
            f"{name} is not set. Export TEMUEU_API, TEMUEU_SECRET and TEMUEU_TOKEN "
            f"before running this client. They must never be written into a file."
        )
    return v


# Resolved lazily: --help and imports must work without credentials present.


def generate_signature(params, app_secret):
    sorted_keys = sorted(k for k in params.keys() if k != "sign")
    concatenated = ""
    for k in sorted_keys:
        v = params[k]
        if isinstance(v, (dict, list)):
            v_str = json.dumps(v, separators=(',', ':'))
        else:
            v_str = str(v)
        concatenated += f"{k}{v_str}"
    
    to_hash = f"{app_secret}{concatenated}{app_secret}"
    return hashlib.md5(to_hash.encode("utf-8")).hexdigest().upper()


def call_temu_api(api_type, business_params=None, endpoint=ENDPOINT_EU):
    all_params = {
        "app_key": _require("TEMUEU_API"),
        "access_token": _require("TEMUEU_TOKEN"),
        "timestamp": int(time.time()),
        "data_type": "JSON",
        "type": api_type,
        "version": "V1",
    }
    
    if business_params:
        all_params.update(business_params)
                
    sign = generate_signature(all_params, _require("TEMUEU_SECRET"))
    all_params["sign"] = sign
    
    post_data = json.dumps(all_params, separators=(',', ':')).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=post_data,
        headers={"Content-Type": "application/json;charset=UTF-8"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(error_body)
        except Exception:
            return {"http_code": e.code, "error": error_body}
    except Exception as e:
        return {"error": str(e)}


def _probe():
    v3_methods = [
        "temu.local.goods.v3.add",
        "temu.local.goods.v3.edit",
        "temu.local.goods.v3.update",
        "temu.local.goods.v3.list.get",
        "temu.local.goods.v3.detail.get",
        "temu.local.goods.v3.cats.get",
        "temu.local.goods.v3.attributes.get",
        "temu.local.goods.v3.template.get",
    ]
    
    print("Testing Temu V3 Product Publishing APIs on EU router:")
    ok = 0
    for m in v3_methods:
        res = call_temu_api(m, {})
        err_msg = res.get("errorMsg", "SUCCESS / OTHER")
        err_code = str(res.get("errorCode", "0"))
        if err_code in ("0", "None"):
            ok += 1
        print(f"[{m}] -> Code: {err_code} | Msg: {err_msg}")
    print(f"\n{ok}/{len(v3_methods)} methods reachable.")
    if ok == 0:
        print("VERDICT: this app_key has no working V3 product permission. Temu is NOT\n"
              "usable as a supplier integration until the permission is granted in the\n"
              "Temu partner console. Authentication succeeding is not the same as access.")
    return 0 if ok else 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Temu Open Platform EU API client")
    ap.add_argument("--probe", action="store_true",
                    help="Call the live EU router to test V3 method permissions")
    a = ap.parse_args()
    if not a.probe:
        # Never hit a production API just because someone asked for help.
        ap.print_help()
        print("\nNo action taken. Pass --probe to make live API calls.")
        raise SystemExit(0)
    raise SystemExit(_probe())
