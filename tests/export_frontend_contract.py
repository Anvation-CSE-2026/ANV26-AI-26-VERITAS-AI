"""Export exact installed API schemas without serializing settings or secrets."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.main import app

if __name__ == "__main__":
    path = ROOT / "docs" / "frontend-openapi.json"
    path.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
    print("Exported docs/frontend-openapi.json")
