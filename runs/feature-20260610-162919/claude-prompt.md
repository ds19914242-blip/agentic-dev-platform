# Feature Request

Translate only the reports page visible UI text to Russian. Do not change logic, APIs, auth, billing, database schema, deployment config or LLM prompts.

# Repository

/Users/danilsmetanev/Projects/rss-agent-lab_2

# Execution Mode

plan_only

# Affected Files

- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/login/page.tsx
- lib/session.ts
- app/reports/page.tsx
- src/config.ts
- src/config/feeds.ts
- src/importers/parseRssTextFile.ts
- app/api/analyze/route.ts
- app/api/benchmark/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts

# Task

Create a detailed implementation plan.

Do not modify files.
Stop after the plan.

# Rules

- Start by inspecting the affected files directly from the repository.
- Prefer the smallest safe implementation.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- If uncertain, stop and explain the uncertainty.
