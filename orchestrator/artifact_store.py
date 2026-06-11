import json
from pathlib import Path

from orchestrator.run_state import attach_artifact


class ArtifactStore:
    def __init__(self, run_dir):
        self.run_dir = Path(run_dir)
        self.artifacts_dir = self.run_dir / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def path(self, name):
        return self.run_dir / name

    def artifact_path(self, name):
        return self.artifacts_dir / name

    def write_json(self, name, data, attach=True):
        path = self.path(name)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

        if attach:
            attach_artifact(self.run_dir, name, path, kind="json")

        return path

    def write_markdown(self, name, content, attach=True):
        path = self.path(name)
        path.write_text(content)

        if attach:
            attach_artifact(self.run_dir, name, path, kind="markdown")

        return path

    def write_text(self, name, content, attach=True):
        path = self.path(name)
        path.write_text(content)

        if attach:
            attach_artifact(self.run_dir, name, path, kind="text")

        return path

    def register_existing(self, name, path, kind="file"):
        attach_artifact(self.run_dir, name, path, kind=kind)
        return path
