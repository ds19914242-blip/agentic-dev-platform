Type: implementation_task
Pipeline: standard
Risk: low
Status: manual_verification_failed

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

## Manual Verification Result

Status: manual_verification_failed
Verified At: 2026-06-12T10:04:50
Note: Reddit option is still missing in Sources UI source type selector
