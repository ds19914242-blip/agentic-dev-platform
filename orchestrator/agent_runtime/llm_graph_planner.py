import json
import os

from orchestrator.agent_runtime.graph_plan import AgentGraphPlan, plan_graph_for_task


def _parse_llm_plan(task, text):
    try:
        data = json.loads(text)
    except Exception:
        return plan_graph_for_task(task)

    lanes = data.get("lanes") or []
    lanes = [lane for lane in lanes if lane in {"backend", "frontend", "qa"}]

    if not lanes:
        lanes = plan_graph_for_task(task).lanes

    return AgentGraphPlan(
        task=task,
        lanes=lanes,
        requires_acceptance=bool(data.get("requires_acceptance", True)),
        requires_release=bool(data.get("requires_release", False)),
    )


def plan_graph(task, repo_path="", product="", use_llm=False):
    if not use_llm and os.environ.get("AGENTIC_USE_LLM_PLANNER") != "1":
        return plan_graph_for_task(task)

    try:
        from orchestrator.claude_executor import run_claude

        prompt = f"""Return ONLY JSON for an agent graph plan.

Task:
{task}

Allowed lanes:
- backend
- frontend
- qa

Schema:
{{
  "lanes": ["frontend"],
  "requires_acceptance": true,
  "requires_release": false
}}
"""
        response = run_claude(
            repo_path=repo_path or ".",
            prompt=prompt,
            allow_writes=False,
            max_turns=2,
            retries=1,
        )
        return _parse_llm_plan(task, response.strip())
    except Exception:
        return plan_graph_for_task(task)
