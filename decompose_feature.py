from pathlib import Path
from datetime import datetime
import re

from orchestrator.product_registry import load_product_config
from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.claude_executor import run_claude


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9а-яё]+", "-", text)
    return text.strip("-")[:60] or "epic"


def make_epic_dir(title):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("backlog") / f"{stamp}-{slugify(title)}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main():
    product_name = input("Product name: ").strip()
    request = input("Big request / epic: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    print(f"Analyzing product: {product_name}")
    print(f"Repo: {repo_path}")

    files = scan_repo(repo_path)
    repo_map = format_repository_map(build_repository_map(files))

    prompt = f"""# Product Analyst Agent

You are creating a feature specification before task decomposition.

Do not modify files.
Do not create implementation tasks yet.

## Product

{product_name}

## Repository

{repo_path}

## Request

{request}

## Repository Map

{repo_map}

## Output

Return markdown with exactly these sections:

# Feature Specification

## Summary

## User Stories

## Acceptance Criteria

Use checkboxes:
- [ ] ...

## Scope

## Out of Scope

## Risks

## Acceptance Scenarios

Use concrete end-to-end user flows. Each scenario should describe actions and expected visible result.

## Manual Verification Scenarios

Use concrete user flows that must be checked manually if automated E2E tests are unavailable.

## Decomposition Notes

Explain how this should later be split into backlog tasks.
"""

    spec = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
    )

    epic_dir = make_epic_dir(request)

    (epic_dir / "epic.md").write_text(f"""# Epic Request

## Product

{product_name}

## Repository

{repo_path}

## Request

{request}
""")

    (epic_dir / "feature-spec.md").write_text(spec)
    (epic_dir / "spec-status.txt").write_text("spec_pending_review\n")

    print(f"Feature spec created: {epic_dir / 'feature-spec.md'}")
    print(f"Epic created: {epic_dir}")
    print()
    print("Review the spec, then run:")
    print(f"python3 agentic.py approve-spec {epic_dir}")


if __name__ == "__main__":
    main()
