# QA Plan

## Feature Request

Show AI summaries in RSS preview before analysis

## Validation Goals

- Confirm the feature works as requested.
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