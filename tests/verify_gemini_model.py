"""List API models, verify structured generation, then optionally set the model."""
import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import errors, types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import settings

# Prevent transport debug logging of credential-bearing requests.
logging.disable(logging.CRITICAL)
SENTENCE = "Supplier shall notify the Company within 48 hours of discovering a data breach."
EXPECTED = {"category": "data_protection", "evidence_quote": SENTENCE, "deadline": "within 48 hours"}
SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["data_protection"]},
        "evidence_quote": {"type": "string"},
        "deadline": {"type": "string"},
    },
    "required": ["category", "evidence_quote", "deadline"],
}


def safe_print(value):
    text = json.dumps(value, ensure_ascii=False)
    if settings.gemini_api_key and settings.gemini_api_key in text:
        raise RuntimeError("Secret redaction check failed.")
    print(text, flush=True)


def update_model(path, model):
    # Preserve every byte outside the model setting, including the key and newlines.
    old = path.read_bytes()
    line = b"GEMINI_MODEL=" + model.encode("ascii")
    pattern = rb"(?m)^[ \t]*GEMINI_MODEL[ \t]*=[^\r\n]*"
    if re.search(pattern, old):
        new = re.sub(pattern, lambda match: line, old)
    else:
        newline = b"\r\n" if b"\r\n" in old else b"\n"
        new = old + (b"" if old.endswith(b"\n") else newline) + line + newline
    path.write_bytes(new)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not settings.gemini_api_key.strip():
        safe_print({"success": False, "reason": "Gemini key is not configured."})
        return 1
    report = {"verified_at": datetime.now(timezone.utc).isoformat(), "models": [], "attempts": [], "success": False}
    with genai.Client(api_key=settings.gemini_api_key,
                      http_options=types.HttpOptions(timeout=60000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
        # Iterate the SDK pager fully, rather than checking only the first page.
        for model in client.models.list():
            name = (model.name or "").removeprefix("models/")
            actions = list(model.supported_actions or [])
            report["models"].append({"model": name, "supported_actions": actions,
                                      "supports_generateContent": "generateContent" in actions})
        safe_print({"listed_models": report["models"]})
        candidates = [item["model"] for item in report["models"] if item["supports_generateContent"] and "flash" in item["model"].lower()
                      and not any(term in item["model"].lower() for term in ["image", "tts", "audio", "live", "native", "robotics"])]
        def rank(name):
            return (name != "gemini-3.8-flash", "lite" in name, "preview" in name, "latest" not in name, name)
        candidates = sorted(set(candidates), key=rank)
        for name in candidates[:6]:
            try:
                response = client.models.generate_content(
                    model=name,
                    contents="Extract the category, exact evidence quote (the entire sentence), and exact deadline from this sentence. Return JSON only: " + SENTENCE,
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=SCHEMA, temperature=0, max_output_tokens=2048),
                )
                actual = json.loads(response.text or "")
                if actual != EXPECTED:
                    report["attempts"].append({"model": name, "success": False, "reason": "Structured output did not match the exact expected evidence and deadline."})
                    safe_print(report["attempts"][-1])
                    continue
                report["selected_model"] = name
                report["response_model_version"] = response.model_version
                report["structured_output"] = actual
                report["success"] = True
                report["attempts"].append({"model": name, "success": True, "json_valid": True, "evidence_exact": True, "deadline_exact": True})
                safe_print(report["attempts"][-1])
                break
            except errors.APIError as exc:
                report["attempts"].append({"model": name, "success": False, "upstream_http": exc.code})
                safe_print(report["attempts"][-1])
                if exc.code in (401, 403):
                    break
            except Exception as exc:
                report["attempts"].append({"model": name, "success": False, "error_type": type(exc).__name__})
                safe_print(report["attempts"][-1])
    report["configuration_updated"] = False
    if report["success"] and args.apply:
        for path in [ROOT / "backend" / ".env", ROOT / "backend" / ".env.example"]:
            update_model(path, report["selected_model"])
        report["configuration_updated"] = True
    serialized = json.dumps(report, indent=2)
    if settings.gemini_api_key in serialized:
        raise RuntimeError("Secret redaction check failed.")
    (ROOT / "docs" / "gemini-model-verification.json").write_text(serialized + "\n", encoding="utf-8")
    safe_print({key: value for key, value in report.items() if key != "models"})
    return 0 if report["success"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # No raw errors, request URLs, tracebacks, or credentials.
        print(json.dumps({"success": False, "error_type": type(exc).__name__}), flush=True)
        raise SystemExit(1)
