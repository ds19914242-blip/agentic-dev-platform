# Feature Request

Translate the RSS application user interface to Russian. Focus only on visible UI text, buttons, labels, empty states and error messages. Do not change business logic, APIs, database schema, auth, billing, deployment config or LLM prompts.

# Repository

/Users/danilsmetanev/Projects/rss-agent-lab_2

# Execution Mode

plan_only

# Affected Files

- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/summarize/route.ts
- app/api/rss/test/route.ts
- app/rss/collections/page.tsx
- app/rss/page.tsx
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/collector/fetchFeeds.ts
- src/config/feeds.ts

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
