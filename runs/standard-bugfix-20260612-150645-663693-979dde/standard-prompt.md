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

### Bug Fix — Recover manual verification failure for task-006

**Problem:** Manual verification failed for `backlog/20260612-144038-добавить-видимый-индикатор-успешной-проверки-источника/task-006.md`.

**Source task:** Task 006 — End-to-end acceptance verification

**Evidence:**
- Manual verification note: Verification toast appears, but persistent verification indicator is not visible on source cards

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- The failed manual verification scenario now passes.
- Existing related behavior still works.
- Validation passes.
- No unrelated files are changed.

**Risk:** medium

## Depends On

task-006

