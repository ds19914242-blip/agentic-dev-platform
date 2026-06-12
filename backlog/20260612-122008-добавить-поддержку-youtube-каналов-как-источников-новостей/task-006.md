Type: implementation_task
Pipeline: standard
Risk: medium
Run: standard-20260612-125500-414403-c78cab
Status: manual_verification_failed

### Task 006 — Sources management UI block

**Goal:** Expose YouTube end-to-end in the sources page so users can add, test, edit, deactivate, and delete YouTube sources.
**Scope:** In the sources page: add YouTube to the type-selector buttons with a Russian label (e.g. "YouTube-канал"); add a YouTube-specific form block (channel input + `maxVideos` + `timeWindowDays` + helper note about pasting channel URL/handle/ID); add the list/display label; repopulate YouTube fields in `startEdit()`; add YouTube validation/parsing to `save()`. Wire Test and Save to the YouTube API branches. Edited limits must persist and re-display correctly after reload.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** YouTube selectable in the type picker with Russian label; form block renders correct inputs + helper note; list shows a YouTube label; `startEdit()` repopulates; `save()` validates and persists; Test surfaces clear errors for invalid input; edit → reload persists values; deactivate excludes from collection and delete removes; other source types' UI unaffected.
**Risk:** medium

## Depends On

task-004, task-005

## Manual Verification Result

Status: manual_verification_failed
Verified At: 2026-06-12T13:33:04
Note: YouTube option is missing in production Sources UI source type selector
