PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/54
Run: standard-20260612-133317-935486-43eb15
Type: implementation_task
Pipeline: standard
Risk: low
Status: manual_verification_failed

### Task 008 — Show YouTube in Sources UI

**Goal:** Make YouTube visible and selectable in the Sources UI.

**Problem:** Production Sources UI shows RSS, Telegram and Reddit, but YouTube is missing.

**Scope:** Sources UI only.

**Acceptance criteria:**
- YouTube appears as a source type option next to RSS, Telegram and Reddit.
- Selecting YouTube shows channel-specific input placeholder, e.g. `@OpenAI` or YouTube channel URL.
- Existing RSS, Telegram and Reddit options still work.
- Validation passes.

**Risk:** low

## Depends On

task-006

## Manual Verification Result

Status: manual_verification_failed
Verified At: 2026-06-12T14:09:26
Note: Production collection returns no articles for YouTube/Reddit sources
Manual Bug Task: backlog/20260612-122008-добавить-поддержку-youtube-каналов-как-источников-новостей/task-010.md
