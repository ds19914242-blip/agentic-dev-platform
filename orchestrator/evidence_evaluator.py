import json
from pathlib import Path


def _read_json(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def evaluate_validator_evidence(epic_dir):
    validation = _read_json(Path(epic_dir) / "validation.json")

    if not validation:
        return {
            "passed": False,
            "reason": "validation.json not found",
            "evidence": [],
        }

    return {
        "passed": validation.get("overall_result") == "passed",
        "reason": f"validation overall_result={validation.get('overall_result')}",
        "evidence": ["validation.json"],
    }


def evaluate_route_evidence(epic_dir):
    route = _read_json(Path(epic_dir) / "route-verification.json")

    if not route:
        return {
            "passed": False,
            "reason": "route-verification.json not found",
            "evidence": [],
        }

    return {
        "passed": route.get("result") == "passed",
        "reason": f"route verification result={route.get('result')}",
        "evidence": ["route-verification.json"],
    }


def evaluate_ui_evidence(epic_dir, note):
    evidence_path = Path(epic_dir) / "verification-evidence.json"

    if not evidence_path.exists():
        return {
            "passed": False,
            "reason": "verification-evidence.json not found",
            "evidence": [],
        }

    if not note.strip():
        return {
            "passed": False,
            "reason": "manual verification note is empty",
            "evidence": ["verification-evidence.json"],
        }

    return {
        "passed": True,
        "reason": "manual UI verification note provided",
        "evidence": ["verification-evidence.json"],
    }


def evaluate_manual_evidence(epic_dir, note):
    if not note.strip():
        return {
            "passed": False,
            "reason": "manual verification note is empty",
            "evidence": [],
        }

    return {
        "passed": True,
        "reason": "manual verification note provided",
        "evidence": ["verification-evidence.json"],
    }


def evaluate_criterion_evidence(epic_dir, verification_type, note):
    if verification_type == "validator":
        return evaluate_validator_evidence(epic_dir)

    if verification_type == "route":
        return evaluate_route_evidence(epic_dir)

    if verification_type == "ui":
        return evaluate_ui_evidence(epic_dir, note)

    return evaluate_manual_evidence(epic_dir, note)
