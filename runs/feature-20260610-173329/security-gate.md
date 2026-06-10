# Security Gate

## Status

needs_approval

## Reason

High-risk files are affected.

## Critical Risk Files

_None_

## High Risk Files

- app/api/feedback/route.ts

## Medium Risk Files

- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/summarize/route.ts
- app/api/rss/test/route.ts
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/collector/fetchFeeds.ts

## Low Risk Files

- app/rss/collections/page.tsx
- app/rss/page.tsx
