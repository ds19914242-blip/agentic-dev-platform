def build_feature_prompt(feature, repo_path, affected, context):
    return f"""# Feature Request

{feature}

# Repository

{repo_path}

# Affected Files

{chr(10).join("- " + f for f in affected)}

# Task

You are a senior autonomous coding agent.

Analyze the affected files and implement the smallest safe solution.

Rules:
- First explain what already exists.
- Then create an implementation plan.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- After implementation, run typecheck/tests if available.
- Summarize changed files and risks.

# Context

{context}
"""
