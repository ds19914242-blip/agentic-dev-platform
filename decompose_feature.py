from pathlib import Path
from datetime import datetime
import re

from orchestrator.product_registry import load_product_config
from orchestrator.claude_executor import run_claude
from orchestrator.product_memory_context import format_product_memory


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9а-яё]+", "-", text)
    return text.strip("-")[:60] or "epic"


def make_epic_dir(title):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("backlog") / f"{stamp}-{slugify(title)}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_product_spec(product_name, repo_path, request, product_memory):
    prompt = f"""# Product Manager Agent

You are the Product Agent for an autonomous development platform.

Your job is to clarify WHAT should be built before any analyst, planner, or engineer decomposes the work.

Do not modify files.
Do not create implementation tasks.
Do not propose code changes.
Do not skip unclear product assumptions; make them explicit.

## Product

{product_name}

## User Request

{request}

## Product Memory

{product_memory}

## Context Boundary

You are intentionally NOT given the repository map, file tree, implementation details, or source code.

Stay at the product layer:
- user/operator problem
- product outcome
- users
- UX/visibility expectations
- success criteria
- acceptance scenarios
- scope boundaries

Do not mention specific files, folders, scripts, functions, classes, package names, commands, database tables, or implementation paths unless they were explicitly present in the user request.

The analyst will receive repository context later and translate this product specification into a technical feature specification.

## Output

Return markdown with exactly these sections:

# Product Specification

## Problem

## Product Goal

## Primary Users

## User Stories

## Functional Requirements

Use checkboxes:
- [ ] ...

## Non-Functional Requirements

Use checkboxes:
- [ ] ...

## UX / Visibility Requirements

## Success Criteria

## Acceptance Scenarios

Use concrete end-to-end product flows:
- Given ...
- When ...
- Then ...

## Out of Scope

## Risks

## Open Questions

List only questions that materially affect scope. If none, write:
None.

## Analyst Handoff
"""

    return run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
    )


def main():
    product_name = input("Product name: ").strip()
    request = input("Big request / epic: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    print(f"Analyzing product: {product_name}")
    print(f"Repo: {repo_path}")

    product_memory = format_product_memory(product_name)

    print("Running Product Agent...")
    product_spec = build_product_spec(
        product_name=product_name,
        repo_path=repo_path,
        request=request,
        product_memory=product_memory,
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

    (epic_dir / "product-spec.md").write_text(product_spec)
    (epic_dir / "product-status.txt").write_text("product_pending_review\n")

    print(f"Product spec created: {epic_dir / 'product-spec.md'}")
    print(f"Epic created: {epic_dir}")
    print()
    print("Review the product spec, then run:")
    print(f"python3 agentic.py approve-product-spec {epic_dir}")


if __name__ == "__main__":
    main()
