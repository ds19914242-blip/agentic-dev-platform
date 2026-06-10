# Architecture Review

## Feature Request

Show AI summaries in RSS preview before analysis

## Review Focus

- Does the feature fit existing architecture?
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

## Initial Risk Assessment

- Risk level: medium
- Reason: code changes may affect user-facing behavior.

## Architecture Rule

Prefer the smallest change that reuses existing modules.
Do not introduce new infrastructure unless required.
