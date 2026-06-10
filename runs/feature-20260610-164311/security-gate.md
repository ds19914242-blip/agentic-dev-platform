# Security Gate

## Status

needs_approval

## Reason

High-risk files are affected.

## Critical Risk Files

_None_

## High Risk Files

- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/api/feedback/route.ts
- app/api/health/db/route.ts

## Medium Risk Files

- src/importers/parseRssTextFile.ts
- app/api/analyze/route.ts
- app/api/benchmark/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts
- app/api/health/route.ts
- app/api/jobs/[jobId]/route.ts

## Low Risk Files

- app/reports/page.tsx
