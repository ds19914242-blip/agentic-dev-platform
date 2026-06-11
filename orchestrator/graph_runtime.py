import json
from pathlib import Path
from datetime import datetime


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


class GraphRuntime:
    def __init__(self, run_dir, run_id=None, product=None, request=None, run_type="feature"):
        self.run_dir = Path(run_dir)
        self.run_id = run_id or self.run_dir.name
        self.product = product
        self.request = request
        self.run_type = run_type
        self.nodes = []

    def add(self, node_id, name):
        existing = self._find_node(node_id)
        if existing:
            return

        self.nodes.append({
            "id": node_id,
            "name": name,
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "updated_at": None,
            "attempt": 0,
            "artifacts": [],
            "error": None,
        })

    def start(self, node_id):
        node = self._find_node(node_id)
        if not node:
            return

        node["status"] = "running"
        node["started_at"] = node["started_at"] or now_iso()
        node["updated_at"] = now_iso()
        node["attempt"] = int(node.get("attempt", 0)) + 1
        node["error"] = None

    def complete(self, node_id, artifacts=None):
        self._set_status(node_id, "completed", artifacts=artifacts)

    def fail(self, node_id, error=None, artifacts=None):
        self._set_status(node_id, "failed", error=error, artifacts=artifacts)

    def skip(self, node_id):
        self._set_status(node_id, "skipped")

    def attach_artifact(self, node_id, artifact):
        node = self._find_node(node_id)
        if not node:
            return

        if artifact not in node["artifacts"]:
            node["artifacts"].append(artifact)

    def _find_node(self, node_id):
        for node in self.nodes:
            if node["id"] == node_id:
                return node
        return None

    def _set_status(self, node_id, status, error=None, artifacts=None):
        node = self._find_node(node_id)
        if not node:
            return

        if status == "completed" and not node.get("started_at"):
            node["started_at"] = now_iso()

        node["status"] = status
        node["updated_at"] = now_iso()

        if status in {"completed", "failed", "skipped"}:
            node["completed_at"] = now_iso()

        if error:
            node["error"] = str(error)

        if artifacts:
            for artifact in artifacts:
                if artifact not in node["artifacts"]:
                    node["artifacts"].append(artifact)

    def current_stage(self):
        running = [node for node in self.nodes if node["status"] == "running"]
        if running:
            return running[-1]["id"]

        unfinished = [
            node for node in self.nodes
            if node["status"] in {"pending", "failed"}
        ]
        if unfinished:
            return unfinished[0]["id"]

        if self.nodes:
            return self.nodes[-1]["id"]

        return None

    def overall_status(self):
        if any(node["status"] == "failed" for node in self.nodes):
            return "failed"

        if self.nodes and all(node["status"] in {"completed", "skipped"} for node in self.nodes):
            return "completed"

        return "running"

    def to_run_state(self):
        return {
            "schema_version": "0.5",
            "run_id": self.run_id,
            "run_type": self.run_type,
            "product": self.product,
            "request": self.request,
            "status": self.overall_status(),
            "current_stage": self.current_stage(),
            "updated_at": now_iso(),
            "stages": {
                node["id"]: {
                    "name": node["name"],
                    "status": node["status"],
                    "started_at": node["started_at"],
                    "completed_at": node["completed_at"],
                    "updated_at": node["updated_at"],
                    "attempt": node["attempt"],
                    "artifacts": node["artifacts"],
                    "error": node["error"],
                }
                for node in self.nodes
            },
        }

    def write_run_json(self):
        path = self.run_dir / "run.json"
        path.write_text(json.dumps(self.to_run_state(), indent=2, ensure_ascii=False))
        return path

    def write_markdown(self):
        lines = ["# Execution Graph v2", ""]

        for node in self.nodes:
            lines.append(f"- [{node['status']}] {node['id']}: {node['name']}")

        path = self.run_dir / "execution-graph-v2.md"
        path.write_text("\n".join(lines))
        return path

    def write(self):
        md_path = self.write_markdown()
        self.write_run_json()
        return md_path
