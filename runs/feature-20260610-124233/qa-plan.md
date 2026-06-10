# QA Plan

## Feature Request

Show AI summaries in RSS preview before analysis

## Based On Plan

# Implementation Plan

## Feature Request

Show AI summaries in RSS preview before analysis

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
- components/BenchmarkTable.tsx
- components/ConfirmModal.tsx
- components/Dashboard.tsx
- components/ErrorState.tsx
- components/ExecutiveSummary.tsx
- components/ExportButtons.tsx

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


## Based On Architecture Review

# Architecture Review

## Feature Request

Show AI summaries in RSS preview before analysis

## Planner Input

# Implementation Plan

## Feature Request

Show AI summaries in RSS preview before analysis

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
- components/BenchmarkTable.tsx
- components/ConfirmModal.tsx
- components/Dashboard.tsx
- components/ErrorState.tsx
- components/ExecutiveSummary.tsx
- components/ExportButtons.tsx

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
- UI component: components/BenchmarkTable.tsx
- UI component: components/ConfirmModal.tsx
- UI component: components/Dashboard.tsx
- UI component: components/ErrorState.tsx
- UI component: components/ExecutiveSummary.tsx
- UI component: components/ExportButtons.tsx

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/summarize/route.ts
- app/api/rss/test/route.ts
- app/rss/collections/page.tsx
- app/rss/page.tsx
- components/BenchmarkTable.tsx
- components/ConfirmModal.tsx
- components/Dashboard.tsx
- components/ErrorState.tsx
- components/ExecutiveSummary.tsx
- components/ExportButtons.tsx

## Required Command

```bash
npx tsc --noEmit
```