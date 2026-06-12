PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/48
Run: standard-bugfix-20260612-100815-275220-18e46d
Type: bug_fix
Pipeline: standard_bugfix
Risk: low
Status: manual_verification_passed

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

## Manual Verification Result

Status: manual_verification_passed
Verified At: 2026-06-12T11:57:06
Note: Reddit option is visible in Sources UI and RSS/Telegram still work
