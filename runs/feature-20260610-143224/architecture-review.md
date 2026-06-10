# Architecture Review

## Feature Request

Translate the RSS application user interface to Russian. Focus only on visible UI text, buttons, labels, empty states and error messages. Do not change business logic, APIs, database schema, auth, billing, deployment config or LLM prompts.

## Planner Input

# Implementation Plan

## Feature Request

Translate the RSS application user interface to Russian. Focus only on visible UI text, buttons, labels, empty states and error messages. Do not change business logic, APIs, database schema, auth, billing, deployment config or LLM prompts.

## Affected Files

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

## Plan

1. Review affected files.
2. Identify existing functionality.
3. Define the smallest safe implementation.
4. Modify only necessary files.
5. Run typecheck or tests.
6. Review git diff.
7. Summarize changes and risks.

## Safety Rules

- Do not modify auth.
- Do not modify billing.
- Do not modify secrets.
- Do not modify database schema unless explicitly required.
- Do not modify deployment configuration.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/rss/collect/route.ts
- API route: app/api/rss/collections/[id]/route.ts
- API route: app/api/rss/collections/route.ts
- API route: app/api/rss/sources/[id]/route.ts
- API route: app/api/rss/sources/route.ts
- API route: app/api/rss/summarize/route.ts
- API route: app/api/rss/test/route.ts
- Other: app/rss/collections/page.tsx
- Other: app/rss/page.tsx
- Library/module: lib/rss/collect.ts
- Library/module: lib/rss/fetchFeed.ts
- Other: src/collector/fetchFeeds.ts
- Other: src/config/feeds.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
