PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/45
Run: standard-20260611-211719-613732-a8e458
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 010 — Wire Reddit fetcher into collection pipeline

**Goal:** Add Reddit fetching to the existing collection flow.

**Scope:** Collector orchestration only.

**Suggested files:** `src/collector/fetchFeeds.ts`, `lib/rss/collect.ts`, `src/config/feeds.ts`

**Acceptance criteria:**
- Reddit sources are fetched through existing collection command/API.
- Existing RSS/Telegram collection behavior remains unchanged.
- Typecheck and build pass.

**Risk:** medium

## Depends On

task-009
