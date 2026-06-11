import json
from pathlib import Path
from datetime import datetime


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def register_artifact(run_dir, name, path=None, kind=None, stage=None):
    run_dir = Path(run_dir)
    run_json = run_dir / "run.json"

    if path is None:
        path = run_dir / name
    else:
        path = Path(path)

    if kind is None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            kind = "json"
        elif suffix in {".md", ".markdown"}:
            kind = "markdown"
        else:
            kind = "file"

    if not run_json.exists():
        return None

    data = json.loads(run_json.read_text())
    timestamp = now_iso()

    data.setdefault("artifacts", {})
    data["artifacts"][name] = {
        "kind": kind,
        "path": str(path),
        "stage": stage,
        "updated_at": timestamp,
    }

    if stage:
        data.setdefault("stages", {})
        if stage in data["stages"]:
            stage_artifacts = data["stages"][stage].setdefault("artifacts", [])
            if name not in stage_artifacts:
                stage_artifacts.append(name)

    data["updated_at"] = timestamp
    run_json.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    return data


def register_artifacts(run_dir, artifacts, stage=None):
    for artifact in artifacts:
        if isinstance(artifact, str):
            register_artifact(run_dir, artifact, stage=stage)
        else:
            register_artifact(
                run_dir,
                artifact["name"],
                path=artifact.get("path"),
                kind=artifact.get("kind"),
                stage=stage or artifact.get("stage"),
            )
