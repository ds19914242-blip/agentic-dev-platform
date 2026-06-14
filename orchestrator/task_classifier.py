import json
from orchestrator.claude_executor import run_claude


ALLOWED_TASK_TYPES = {
    "micro_change",
    "bug_fix",
    "implementation_task",
    "feature_task",
    "audit_task",
    "verification_task",
}

ALLOWED_PIPELINES = {
    "fast",
    "standard_bugfix",
    "standard",
    "full",
    "audit",
    "acceptance_verification",
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

    lowered_task = task_text.lower()
    if (
        "end-to-end acceptance verification" in lowered_task
        or "manual verification scenarios" in lowered_task
        or "acceptance scenarios pass" in lowered_task
    ):
        return {
            "task_type": "verification_task",
            "pipeline": "acceptance_verification",
            "risk": "medium",
            "reason": "End-to-end acceptance verification task",
        }

    prompt = f"""Classify this executable task.

Return ONLY valid JSON:

{{
  "task_type": "micro_change | bug_fix | implementation_task | feature_task | audit_task | verification_task",
  "pipeline": "fast | standard_bugfix | standard | full | audit | acceptance_verification",
  "risk": "low | medium | high",
  "reason": ""
}}

Definitions:
- verification_task: end-to-end acceptance/product verification task, especially tasks titled "End-to-end acceptance verification" or containing "Manual Verification Scenarios"
- micro_change: tiny text/copy/label/typo/UI wording change
- bug_fix: known broken behavior or exception that should be fixed
- implementation_task: bounded change to existing page/component/module
- feature_task: part of a new feature or larger behavior
- audit_task: scan/sweep/check for remaining issues and create follow-up tasks

Pipeline mapping:
- verification_task -> acceptance_verification
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
