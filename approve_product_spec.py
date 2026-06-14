from pathlib import Path
import argparse
import re

from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.claude_executor import run_claude


def extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_epic(epic_dir):
    epic_md = Path(epic_dir) / "epic.md"
    text = epic_md.read_text(errors="ignore")

    product = extract_section(text, "Product")
    repo = extract_section(text, "Repository")
    request = extract_section(text, "Request")

    if not product or not repo or not request:
        raise RuntimeError(f"Could not parse epic.md: {epic_md}")

    return product, repo, request


def build_feature_spec(product_name, repo_path, request, product_spec, repo_map):
    prompt = f"""# Product Analyst Agent

You are creating a feature specification before task decomposition.

You must use the approved Product Specification as the source of truth.
Do not bypass product intent.
Do not modify files.
Do not create implementation tasks yet.

## Product

{product_name}

## Repository

{repo_path}

## Original User Request

{request}

## Approved Product Specification

{product_spec}

## Repository Map

{repo_map}

## Output

Return markdown with exactly these sections:

# Feature Specification

## Summary

## Product Context

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
"""

    return run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epic_dir")
    args = parser.parse_args()

    epic_dir = Path(args.epic_dir)
    product_spec_path = epic_dir / "product-spec.md"
    product_status_path = epic_dir / "product-status.txt"

    if not product_spec_path.exists():
        raise RuntimeError(f"product-spec.md not found: {product_spec_path}")

    status = product_status_path.read_text(errors="ignore").strip() if product_status_path.exists() else ""

    if status == "product_approved" and (epic_dir / "feature-spec.md").exists():
        print(f"Product spec already approved: {epic_dir}")
        print(f"Feature spec already exists: {epic_dir / 'feature-spec.md'}")
        return

    product, repo_path, request = parse_epic(epic_dir)
    product_spec = product_spec_path.read_text(errors="ignore")

    print(f"Approving product spec: {epic_dir}")
    print(f"Analyzing repository: {repo_path}")

    files = scan_repo(repo_path)
    repo_map = format_repository_map(build_repository_map(files))

    # Step-0 reuse: prepend the stored Repository Analyst output if present,
    # so the Analyst builds on the existing codebase analysis instead of only
    # the raw file map.
    try:
        from orchestrator.product_memory_context import format_codebase_analysis
        analysis = format_codebase_analysis(product)
        if analysis:
            repo_map = analysis + "\n\n---\n\n" + repo_map
    except Exception:
        pass

    feature_spec = build_feature_spec(
        product_name=product,
        repo_path=repo_path,
        request=request,
        product_spec=product_spec,
        repo_map=repo_map,
    )

    (epic_dir / "feature-spec.md").write_text(feature_spec)
    (epic_dir / "product-status.txt").write_text("product_approved\n")
    (epic_dir / "spec-status.txt").write_text("spec_pending_review\n")

    print(f"Product spec approved: {epic_dir}")
    print(f"Feature spec created: {epic_dir / 'feature-spec.md'}")
    print()
    print("Review the feature spec, then run:")
    print(f"python3 agentic.py approve-spec {epic_dir}")


if __name__ == "__main__":
    main()
