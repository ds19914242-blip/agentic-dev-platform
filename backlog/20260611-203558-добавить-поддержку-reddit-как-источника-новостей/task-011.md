PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/46
Run: standard-20260611-212052-737513-2a7de3
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 011 — Store collected Reddit articles

**Goal:** Persist normalized Reddit articles through the existing storage layer.

**Scope:** Storage integration only.

**Suggested files:** `lib/storage/rss.ts`, `lib/storage/local.ts`, `lib/storage/types.ts`

**Acceptance criteria:**
- Reddit articles can be stored and read with existing article flows.
- Deduplication remains stable.
- Existing article storage behavior remains unchanged.
- Typecheck and build pass.

**Risk:** medium

## Depends On

task-010
