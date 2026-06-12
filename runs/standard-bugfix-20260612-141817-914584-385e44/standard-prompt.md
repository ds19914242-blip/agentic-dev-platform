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

### Bug Fix — Recover manual verification failure for task-010

**Problem:** Manual verification failed for `backlog/20260612-122008-добавить-поддержку-youtube-каналов-как-источников-новостей/task-010.md`.

**Source task:** task-010.md

**Evidence:**
- Manual verification note: Production still shows no articles collected after PR #56

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- The failed manual verification scenario now passes.
- Existing related behavior still works.
- Validation passes.
- No unrelated files are changed.

**Risk:** medium

## Depends On

task-010

