# Implementation Plan

## Feature Request

Add a small Russian helper text under the sources page title explaining that RSS sources can be added and tested here

## Affected Files

- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/rss/collections/page.tsx
- src/collector/fetchFeeds.ts
- app/sources/page.tsx
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/importers/parseRssTextFile.ts
- app/api/feedback/route.ts

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
