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

