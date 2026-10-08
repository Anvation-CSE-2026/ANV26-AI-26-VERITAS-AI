"""Display the precomputed synthetic snapshot; never a live-analysis fallback."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.demo import load_demo


def demonstration():
    artifact = load_demo()
    return {
        "output_origin": artifact.output_origin, "live_ai_used": artifact.live_ai_used,
        "label": artifact.label, "description": artifact.description,
        "contract_id": artifact.contract.contract_id, "analysis_id": artifact.analysis.analysis_id,
        "findings": [item.model_dump(mode="json") for item in artifact.analysis.findings],
        "obligations": [item.model_dump(mode="json") for item in artifact.analysis.obligations],
        "requires_human_review": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    result = demonstration()
    if not args.full:
        counts = {"findings_count": len(result["findings"]), "obligations_count": len(result["obligations"])}
        result = {key: value for key, value in result.items() if key not in ("findings", "obligations")}
        result.update(counts)
    print(json.dumps(result, indent=2, ensure_ascii=True))
