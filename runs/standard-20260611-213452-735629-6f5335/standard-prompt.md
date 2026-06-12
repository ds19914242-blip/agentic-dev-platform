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

### Task 012 — Show Reddit as a source type in Sources UI

**Goal:** Make Reddit selectable when adding a new source.

**Problem:** Reddit support was added in backend/types, but the Sources UI still only shows RSS feed and Telegram channel.

**Scope:** Sources UI only.

**Suggested files:** `components/SourcePicker.tsx`, source form components, Sources page components.

**Acceptance criteria:**
- The new source form shows Reddit as a selectable source type.
- Selecting Reddit changes the input label/placeholder to subreddit format, e.g. `r/OpenAI`.
- Existing RSS and Telegram source options still work.
- Validation passes.

**Risk:** low

## Depends On

_None_

