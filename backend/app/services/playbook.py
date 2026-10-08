from pathlib import Path

from app.models.contracts import Playbook

PLAYBOOK_PATH = Path(__file__).resolve().parents[1] / "resources" / "sample_playbook.json"


def load_playbook() -> Playbook:
    playbook = Playbook.model_validate_json(PLAYBOOK_PATH.read_text(encoding="utf-8"))
    ids = [rule.policy_id for rule in playbook.rules]
    if len(ids) != len(set(ids)):
        raise ValueError("Playbook IDs must be unique.")
    return playbook
