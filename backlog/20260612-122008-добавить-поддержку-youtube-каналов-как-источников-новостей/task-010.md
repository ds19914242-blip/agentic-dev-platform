PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/56
Run: standard-bugfix-20260612-140941-772285-0f7d1b
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Status: manual_verification_failed
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

## Manual Verification Result

Status: manual_verification_failed
Verified At: 2026-06-12T14:18:04
Note: Production still shows no articles collected after PR #56
Manual Bug Task: backlog/20260612-122008-добавить-поддержку-youtube-каналов-как-источников-новостей/task-011.md
