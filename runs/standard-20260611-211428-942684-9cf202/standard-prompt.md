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

