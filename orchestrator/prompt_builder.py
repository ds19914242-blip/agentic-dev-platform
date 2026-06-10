def build_feature_prompt(feature, repo_path, affected, context, mode="plan_only"):
    if mode == "implement":
        task = """Analyze the affected files and implement the smallest safe solution.

You are allowed to modify files.

After implementation:
- run typecheck/tests if available
- summarize changed files
- summarize risks
- stop after implementation and validation"""
    else:
        task = """Analyze the affected files and create a detailed implementation plan.

Do not modify files yet.
Stop after the plan."""

    return f"""# Feature Request

{feature}

# Repository

{repo_path}

# Execution Mode

{mode}

# Affected Files

{chr(10).join("- " + f for f in affected)}

# Task

You are a senior autonomous coding agent.

{task}

Rules:
- First explain what already exists.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- If uncertain, stop and explain the uncertainty.

# Context

{context}
"""
