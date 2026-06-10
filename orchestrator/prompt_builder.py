def build_feature_prompt(feature, repo_path, affected, context, mode="plan_only"):
    affected_list = chr(10).join("- " + f for f in affected)

    if mode == "implement":
        task = """Implement the feature directly in the repository.

You may read files as needed.

You are allowed to modify files.

After implementation:
- run npx tsc --noEmit if this is a TypeScript project
- summarize changed files
- summarize risks
- stop after implementation and validation"""
    else:
        task = """Create a detailed implementation plan.

Do not modify files.
Stop after the plan."""

    return f"""# Feature Request

{feature}

# Repository

{repo_path}

# Execution Mode

{mode}

# Affected Files

{affected_list}

# Task

{task}

# Rules

- Start by inspecting the affected files directly from the repository.
- Prefer the smallest safe implementation.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- If uncertain, stop and explain the uncertainty.
"""
