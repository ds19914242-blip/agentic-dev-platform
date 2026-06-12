# Standard Task Execution

You are fixing a known bug.

Steps:
1. Identify the likely root cause.
2. Make the smallest safe fix.
3. Do not redesign unrelated code.
4. Preserve existing behavior except for the bug.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: bug_fix
Pipeline: standard_bugfix
Risk: low
Status: in_progress

### Task 014 — Fix Reddit option missing in Sources UI

**Goal:** Make Reddit visible and selectable in the Sources UI.

**Problem:** Manual verification failed: Reddit option is still missing in the source type selector.

**Scope:** Sources UI only.

**Acceptance criteria:**
- Reddit appears as a source type option next to RSS and Telegram.
- Selecting Reddit shows subreddit-specific copy/placeholder, for example `r/OpenAI`.
- Existing RSS and Telegram options still work.
- Validation passes.

**Risk:** low

## Depends On

task-012

