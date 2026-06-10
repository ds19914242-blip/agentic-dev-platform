# Implementation Plan

## Feature Request

Add a small note in RSS preview explaining that AI summaries are optional

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
