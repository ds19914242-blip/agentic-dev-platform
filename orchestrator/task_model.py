from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from orchestrator.task_status import TaskStatus, normalize_status


FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z _-]*):\s*(.*)$")


def canonical_field_name(name):
    return name.strip().replace("_", " ").replace("-", " ").title().replace(" ", "")


@dataclass
class TaskDocument:
    path: Path
    text: str

    @property
    def fields(self):
        result = {}

        for line in self.text.splitlines():
            match = FIELD_RE.match(line)
            if not match:
                continue

            result[canonical_field_name(match.group(1))] = match.group(2).strip()

        return result

    @property
    def status(self):
        return normalize_status(self.fields.get("Status"))

    @property
    def title(self):
        for line in self.text.splitlines():
            line = line.strip()
            if line.startswith("### Task "):
                return line.replace("### ", "").strip()

        lines = [line.strip() for line in self.text.splitlines() if line.strip()]
        return lines[0] if lines else self.path.name

    @property
    def pr_url(self):
        return self.fields.get("Pr", "") or self.fields.get("PR", "")

    @property
    def run_id(self):
        return self.fields.get("Run", "")

    def set_status(self, status):
        if isinstance(status, TaskStatus):
            status = status.value
        self.set_field("Status", str(status))

    def set_field(self, field_name, value):
        canonical = canonical_field_name(field_name)
        display_name = "PR" if canonical.lower() == "pr" else canonical
        replacement = f"{display_name}: {value}"

        lines = self.text.splitlines()
        updated = []
        found = False

        for line in lines:
            match = FIELD_RE.match(line)
            if match and canonical_field_name(match.group(1)).lower() == canonical.lower():
                updated.append(replacement)
                found = True
            else:
                updated.append(line)

        if not found:
            updated = [replacement] + updated

        self.text = "\n".join(updated).rstrip() + "\n"

    def remove_fields(self, field_names):
        names = {canonical_field_name(name).lower() for name in field_names}
        lines = []

        for line in self.text.splitlines():
            match = FIELD_RE.match(line)
            if match and canonical_field_name(match.group(1)).lower() in names:
                continue
            lines.append(line)

        self.text = "\n".join(lines).rstrip() + "\n"
