PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/52
Run: standard-20260612-123234-413957-cf998e
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 003 — Collection dispatch branch

**Goal:** Wire YouTube sources into the collection pipeline.
**Scope:** Add a dispatch branch in the collector for `type === "youtube" && src.youtube` that calls `fetchYouTubeChannel()` and feeds results into the same aggregation path as other source types. Tiny glue task.
**Suggested files:** `lib/rss/collect.ts`
**Acceptance criteria:** A source with `sourceType: "youtube"` and a populated `youtube` config is collected via the new fetcher; RSS/Telegram/Reddit branches unchanged; mixed collections aggregate all types together; TypeScript compiles.
**Risk:** low

## Depends On

task-001, task-002
