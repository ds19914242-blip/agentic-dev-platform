PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/44
Run: standard-20260611-211428-942684-9cf202
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 009 — Normalize Reddit posts into article model

**Goal:** Define how Reddit posts map into the existing article/source model.

**Scope:** Types and normalization only.

**Suggested files:** `lib/reddit/*`, `src/types/article.ts`, `lib/storage/types.ts`

**Acceptance criteria:**
- Reddit post fields map to existing article fields.
- Source type is preserved as reddit.
- No collector orchestration changes.
- Typecheck passes.

**Risk:** medium

## Depends On

task-001, task-002
