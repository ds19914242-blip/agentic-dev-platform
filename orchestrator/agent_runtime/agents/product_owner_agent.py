import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.agent_runtime.platform_systems import write_runtime_json, write_runtime_markdown


class ProductOwnerAgent(Agent):
    name = "product_owner"

    def run(self, context: AgentContext) -> AgentResult:
        task = context.task
        analysis = context.inputs.get("analysis_context", {})
        affected = analysis.get("affected_files", [])

        decision = {
            "task": task,
            "product_goal": "Preserve the core RSS workflow and remove user-facing complexity.",
            "scope": {
                "keep_source_types": ["rss", "telegram", "youtube"],
                "navigation_keep": [
                    "dashboard",
                    "sources",
                    "collections",
                    "reports",
                    "settings",
                    "login",
                    "register",
                ],
                "navigation_remove_from_menu": [
                    "workspace",
                    "templates",
                    "history",
                    "benchmark",
                    "profiles",
                    "summary",
                    "reading-list",
                    "feedback",
                    "admin/users",
                ],
            },
            "rules": [
                "Do not delete routes unless explicitly requested.",
                "Remove or hide unsupported source types only from user-facing UI.",
                "Keep backend compatibility unless a source type is truly unused.",
                "Preserve typecheck and build.",
                "No unrelated visual redesign.",
            ],
            "acceptance_criteria": [
                "Sources UI offers only RSS, Telegram, and YouTube as source types.",
                "Navigation shows only core workflow pages.",
                "No links to unused pages remain in main navigation.",
                "Existing RSS source collection still works.",
                "Typecheck and build pass.",
            ],
            "affected_files": affected,
        }

        md = (
            "# Product Owner Decision\n\n"
            f"## Task\n\n{task}\n\n"
            "## Product Goal\n\n"
            f"{decision['product_goal']}\n\n"
            "## Keep Source Types\n\n"
            + "\n".join(f"- {item}" for item in decision["scope"]["keep_source_types"])
            + "\n\n## Keep Navigation\n\n"
            + "\n".join(f"- {item}" for item in decision["scope"]["navigation_keep"])
            + "\n\n## Remove From Navigation\n\n"
            + "\n".join(f"- {item}" for item in decision["scope"]["navigation_remove_from_menu"])
            + "\n\n## Rules\n\n"
            + "\n".join(f"- {item}" for item in decision["rules"])
            + "\n\n## Acceptance Criteria\n\n"
            + "\n".join(f"- {item}" for item in decision["acceptance_criteria"])
            + "\n"
        )

        artifacts = []

        if context.run_dir:
            md_path = write_runtime_markdown(
                context.run_dir,
                "product-owner-decision.md",
                md,
                stage="product_owner",
            )
            json_path = write_runtime_json(
                context.run_dir,
                "product-owner-decision.json",
                decision,
                stage="product_owner",
            )
            artifacts = [str(md_path), str(json_path)]

        return AgentResult(
            status="completed",
            confidence=0.8,
            artifacts=artifacts,
            findings=[
                "Product owner decision created",
                "Source types limited to RSS, Telegram, YouTube",
                "Navigation simplification scope defined",
            ],
            handoff={"product_owner_decision": decision},
        )
