"""
Repository Analyst — step 0 of the platform.

When a repository is connected, this agent reads the codebase once and writes a
human-readable analysis (stack, architecture, subsystems, conventions, risks)
into the product's memory so later agents (the Product Analyst at
approve-product-spec, runtime agents) can reuse it instead of re-discovering
the repo every time.

Storage (all under memory/):
- memory/<product>-analysis.md                 full markdown analysis
- memory/<product>-architecture-memory.json    appended record (existing slot)
- memory/<product>-product-memory.json         compact codebase_summary

CLI:  python3 agentic.py analyze <product> [--no-write]
"""

import re
from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.claude_executor import run_claude
from orchestrator.memory_store import (
    MEMORY_DIR,
    ensure_memory_dir,
    append_architecture_memory,
    update_product_memory,
)


def _section(text, heading):
    m = re.search(rf"##\s*{re.escape(heading)}\s*\n+(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def build_analysis_prompt(product_name, repo_path, repo_map):
    return f"""# Repository Analyst Agent

You are analyzing an existing codebase so that later agents can plan and
implement changes safely. You may read any files you need.

Do not modify files. Do not propose changes. Describe what exists.

## Product

{product_name}

## Repository

{repo_path}

## Repository Map (auto-generated, partial)

{repo_map}

## Output

Return markdown with exactly these sections:

# Codebase Analysis

## Stack
Languages, framework, key libraries, package manager, build/test tooling.

## Architecture
The high-level shape: layers, how the app is structured, how data flows.

## Key Subsystems
The main modules/areas and what each is responsible for.

## Entry Points
Where the app starts; main routes, pages, or commands.

## Conventions
Naming, file layout, and patterns a contributor must follow.

## Where Changes Usually Go
For a UI change / an API change / a data-model change — which files or folders.

## Risks & Constraints
Fragile or must-not-touch areas (auth, billing, schema, secrets, deploy).

## Summary
3-5 plain-language sentences describing the project.
"""


def _fallback_analysis(product_name, repo_path, repo_map, reason):
    return (
        "# Codebase Analysis\n\n"
        f"> Repository Analyst could not run the LLM step: {reason}.\n"
        "> Below is the deterministic repository map only. Re-run on a machine "
        "with the `claude` CLI for the full analysis.\n\n"
        f"## Summary\n\nAuto-generated map for {product_name} at {repo_path}.\n\n"
        + repo_map
    )


def analyze_repository(product_name, write=True):
    """Run the Repository Analyst for a product. Returns a structured result."""
    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    files = scan_repo(repo_path)
    repo_map = format_repository_map(build_repository_map(files))
    prompt = build_analysis_prompt(product_name, repo_path, repo_map)

    agent_ran = True
    try:
        analysis_md = run_claude(
            repo_path=repo_path, prompt=prompt, allow_writes=False, max_turns=12,
        )
    except FileNotFoundError:
        agent_ran = False
        analysis_md = _fallback_analysis(product_name, repo_path, repo_map, "`claude` CLI not found")
    except Exception as exc:
        agent_ran = False
        analysis_md = _fallback_analysis(product_name, repo_path, repo_map, str(exc))

    summary = _section(analysis_md, "Summary")
    stack = _section(analysis_md, "Stack")

    record = {
        "product": product_name,
        "repo_path": repo_path,
        "file_count": len(files),
        "agent_ran": agent_ran,
        "summary": summary,
        "analysis_md": analysis_md,
    }

    if write:
        ensure_memory_dir()
        analysis_path = MEMORY_DIR / f"{product_name}-analysis.md"
        analysis_path.write_text(analysis_md)

        append_architecture_memory(product_name, {
            "kind": "codebase_analysis",
            "repo_path": repo_path,
            "file_count": len(files),
            "summary": summary,
            "agent_ran": agent_ran,
        })

        update_product_memory(product_name, {
            "framework": product.get("framework", ""),
            "codebase_summary": summary,
            "codebase_stack": stack,
            "analysis_file": f"memory/{product_name}-analysis.md",
        })

        record["analysis_path"] = str(analysis_path)

    return record
