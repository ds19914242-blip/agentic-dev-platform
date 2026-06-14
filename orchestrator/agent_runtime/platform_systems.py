import json
from pathlib import Path

from orchestrator.artifact_store import ArtifactStore
from orchestrator.run_artifacts import register_artifact


def write_runtime_markdown(run_dir, name, content, stage=None):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        path = ArtifactStore(run_dir).write_markdown(name, content)
    except Exception:
        path = run_dir / name
        path.write_text(content)

    try:
        register_artifact(run_dir, name, path=path, kind="markdown", stage=stage)
    except Exception:
        pass

    return path


def write_runtime_json(run_dir, name, data, stage=None):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        path = ArtifactStore(run_dir).write_json(name, data)
    except Exception:
        path = run_dir / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    try:
        register_artifact(run_dir, name, path=path, kind="json", stage=stage)
    except Exception:
        pass

    return path


def register_runtime_existing(run_dir, name, path, kind="file", stage=None):
    run_dir = Path(run_dir)

    try:
        ArtifactStore(run_dir).register_existing(name, path, kind=kind)
    except Exception:
        pass

    try:
        register_artifact(run_dir, name, path=path, kind=kind, stage=stage)
    except Exception:
        pass

    return path
