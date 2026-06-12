PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/62
Run: standard-bugfix-20260612-150645-663693-979dde
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Status: pr_created
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
