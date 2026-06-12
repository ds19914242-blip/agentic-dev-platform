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
Risk: low
Status: in_progress

### Task 003 — Collection dispatch branch

**Goal:** Wire YouTube sources into the collection pipeline.
**Scope:** Add a dispatch branch in the collector for `type === "youtube" && src.youtube` that calls `fetchYouTubeChannel()` and feeds results into the same aggregation path as other source types. Tiny glue task.
**Suggested files:** `lib/rss/collect.ts`
**Acceptance criteria:** A source with `sourceType: "youtube"` and a populated `youtube` config is collected via the new fetcher; RSS/Telegram/Reddit branches unchanged; mixed collections aggregate all types together; TypeScript compiles.
**Risk:** low

## Depends On

task-001, task-002

