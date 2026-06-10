from orchestrator.claude_executor import run_claude


def create_llm_plan(repo_path, feature, affected_files, repo_map_text):
    affected = "\n".join("- " + f for f in affected_files)

    prompt = f"""# Planner Agent

You are the Planner Agent for an autonomous development platform.

Create a concise implementation plan.

Do not modify files.

## Feature Request

{feature}

## Affected Files

{affected}

## Repository Map

{repo_map_text}

## Output Format

Return:

# Implementation Plan

## Summary

## Files To Inspect

## Implementation Steps

## Validation Steps

## Risks
"""

    return run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=5,
    )
