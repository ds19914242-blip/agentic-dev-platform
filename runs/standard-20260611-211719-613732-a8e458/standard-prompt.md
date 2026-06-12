# Standard Task Execution

You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: implementation_task
Pipeline: standard
Risk: medium
Status: in_progress

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

