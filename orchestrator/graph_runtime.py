from pathlib import Path
from datetime import datetime


class GraphRuntime:
    def __init__(self, run_dir):
        self.run_dir = Path(run_dir)
        self.nodes = []

    def add(self, node_id, name):
        self.nodes.append({
            "id": node_id,
            "name": name,
            "status": "pending",
            "updated_at": None,
        })

    def complete(self, node_id):
        self._set_status(node_id, "completed")

    def fail(self, node_id):
        self._set_status(node_id, "failed")

    def skip(self, node_id):
        self._set_status(node_id, "skipped")

    def _set_status(self, node_id, status):
        for node in self.nodes:
            if node["id"] == node_id:
                node["status"] = status
                node["updated_at"] = datetime.now().isoformat()
                break

    def write(self):
        lines = ["# Execution Graph v2", ""]

        for node in self.nodes:
            lines.append(f"- [{node['status']}] {node['id']}: {node['name']}")

        path = self.run_dir / "execution-graph-v2.md"
        path.write_text("\n".join(lines))
        return path
