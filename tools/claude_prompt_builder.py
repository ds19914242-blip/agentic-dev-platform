# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path
import subprocess

REPO_PATH = "/Users/danilsmetanev/Projects/rss-agent-lab_2"
PROMPT_OUT = "runs/claude-code-feature-prompt.md"

AFFECTED_FILES = [
    "app/api/rss/collect/route.ts",
    "app/rss/page.tsx",
    "lib/rss/collect.ts",
    "lib/rss/fetchFeed.ts",
    "src/llm/client.ts",
    "src/agents/criteriaBatchAgent.ts",
    "src/agents/trendAnalysisAgent.ts",
]

def read_file(path):
    full = Path(REPO_PATH) / path
    if full.exists():
        return f"\n\n# FILE: {path}\n\n" + full.read_text(errors="ignore")[:8000]
    return ""

def main():
    sections = []

    for file in AFFECTED_FILES:
        sections.append(read_file(file))

    prompt = f"""You are a senior autonomous coding agent.

Feature request:
Add AI summaries to RSS feed items.

Repository:
{REPO_PATH}

Relevant files:
{chr(10).join("- " + f for f in AFFECTED_FILES)}

Task:
1. Analyze the provided files.
2. Identify the smallest safe implementation.
3. Modify the repository directly.
4. Prefer existing LLM utilities if available.
5. Run typecheck or tests if available.
6. Summarize changes and risks.

Rules:
- Do not modify auth, billing, secrets, or production config.
- Do not change database schema unless absolutely necessary.
- Keep changes small and reversible.

Context:
{''.join(sections)}
"""

    Path("runs").mkdir(exist_ok=True)
    Path(PROMPT_OUT).write_text(prompt)

    print(f"Claude Code prompt created: {PROMPT_OUT}")

if __name__ == "__main__":
    main()
