"""Safe connectivity diagnostic: never print keys, URLs with keys, or raw errors."""
import json
import socket
import sys
from pathlib import Path

import httpx
from google import genai
from google.genai import errors, types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import settings


def main():
    print(json.dumps({"key_configured": bool(settings.gemini_api_key.strip()), "model": settings.gemini_model}))
    try:
        socket.getaddrinfo("generativelanguage.googleapis.com", 443)
        print("Google API DNS: resolved")
    except OSError:
        print("Google API DNS: failed")
    for trust_env in (True, False):
        try:
            with httpx.Client(timeout=15, trust_env=trust_env) as client:
                response = client.get("https://generativelanguage.googleapis.com/")
                print(json.dumps({"unauthenticated_https": response.status_code, "trust_env": trust_env}))
        except Exception as exc:
            # Classify locally without exposing raw details or credential-bearing URLs.
            print(json.dumps({"unauthenticated_https_error": type(exc).__name__, "trust_env": trust_env,
                              "certificate_related": "CERTIFICATE_VERIFY_FAILED" in str(exc)}))
    try:
        with genai.Client(api_key=settings.gemini_api_key, http_options=types.HttpOptions(timeout=15000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
            model = client.models.get(model=settings.gemini_model)
            print(json.dumps({"gemini_model_lookup": "success", "configured_model_available": bool(model.name)}))
    except errors.APIError as exc:
        print(json.dumps({"gemini_model_lookup": "API error", "status_code": exc.code}))
    except Exception as exc:
        print(json.dumps({"gemini_model_lookup": "transport error", "exception_type": type(exc).__name__,
                          "certificate_related": "CERTIFICATE_VERIFY_FAILED" in str(exc)}))


if __name__ == "__main__":
    main()
