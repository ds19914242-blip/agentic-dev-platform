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
Risk: medium
Status: in_progress
Source: manual_verification_failed

### Bug Fix — Recover manual verification failure for task-008

**Problem:** Manual verification failed for `backlog/20260612-122008-добавить-поддержку-youtube-каналов-как-источников-новостей/task-008.md`.

**Source task:** Task 008 — Show YouTube in Sources UI

**Evidence:**
- Manual verification note: Production collection returns no articles for YouTube/Reddit sources

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- The failed manual verification scenario now passes.
- Existing related behavior still works.
- Validation passes.
- No unrelated files are changed.

**Risk:** medium

## Depends On

task-008

