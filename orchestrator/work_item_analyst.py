import json
from orchestrator.claude_executor import run_claude


ALLOWED_TYPES = {"feature", "bug", "epic", "research", "spike"}


def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    return None


def analyze_work_item(repo_path, request):
    prompt = f"""Classify this work item.

Return ONLY valid JSON:

{{
  "work_item_type": "feature | bug | epic | research | spike",
  "reason": "",
  "should_decompose": true
}}

Definitions:
- feature: single product/platform change
- bug: reported problem or broken behavior
- epic: large container that should be decomposed into tasks
- research: investigation/recommendation, no code changes
- spike: prototype/proof-of-concept

Request:
{request}
"""

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=3,
        retries=1,
    )

    data = parse_json(response) or {
        "work_item_type": "feature",
        "reason": "Fallback classification",
        "should_decompose": False,
    }

    if data.get("work_item_type") not in ALLOWED_TYPES:
        data["work_item_type"] = "feature"

    data["should_decompose"] = bool(
        data.get("should_decompose") or data["work_item_type"] == "epic"
    )

    return data
