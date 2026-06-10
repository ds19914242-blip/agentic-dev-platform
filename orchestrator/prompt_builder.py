def build_feature_prompt(feature, repo_path, affected, context):
    return f"""# Feature Request

{feature}

# Repository

{repo_path}

# Affected Files

{chr(10).join("- " + f for f in affected)}

# Task

You are a senior autonomous coding agent.

Analyze the affected files and create a detailed implementation plan. Do not modify files yet.

Rules:
- First explain what already exists.
- Then create an implementation plan.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- Do not run implementation yet. Stop after the plan.
- Summarize changed files and risks.

# Context

{context}
"""
