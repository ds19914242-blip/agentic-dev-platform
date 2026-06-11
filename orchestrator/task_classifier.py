import json
from orchestrator.claude_executor import run_claude


ALLOWED_TASK_TYPES = {
    "micro_change",
    "bug_fix",
    "implementation_task",
    "feature_task",
    "audit_task",
}

ALLOWED_PIPELINES = {
    "fast",
    "standard_bugfix",
    "standard",
    "full",
    "audit",
}


def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    return None


def classify_task(repo_path, task_text):
    prompt = f"""Classify this executable task.

Return ONLY valid JSON:

{{
  "task_type": "micro_change | bug_fix | implementation_task | feature_task | audit_task",
  "pipeline": "fast | standard_bugfix | standard | full | audit",
  "risk": "low | medium | high",
  "reason": ""
}}

Definitions:
- micro_change: tiny text/copy/label/typo/UI wording change
- bug_fix: known broken behavior or exception that should be fixed
- implementation_task: bounded change to existing page/component/module
- feature_task: part of a new feature or larger behavior
- audit_task: scan/sweep/check for remaining issues and create follow-up tasks

Pipeline mapping:
- micro_change -> fast
- bug_fix -> standard_bugfix
- implementation_task -> standard
- feature_task -> full
- audit_task -> audit

Task:
{task_text}
"""

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=3,
        retries=1,
    )

    data = parse_json(response) or {
        "task_type": "implementation_task",
        "pipeline": "standard",
        "risk": "medium",
        "reason": "Fallback classification",
    }

    if data.get("task_type") not in ALLOWED_TASK_TYPES:
        data["task_type"] = "implementation_task"

    if data.get("pipeline") not in ALLOWED_PIPELINES:
        data["pipeline"] = "standard"

    if data.get("risk") not in {"low", "medium", "high"}:
        data["risk"] = "medium"

    return data
