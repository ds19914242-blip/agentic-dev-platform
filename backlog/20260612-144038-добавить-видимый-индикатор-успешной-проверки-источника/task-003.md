PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/61
Run: standard-20260612-144849-513929-31fb4c
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 003 — Accessibility pass on the indicator

**Goal:** Ensure the check indicator conveys status via text/aria/icon, not color alone, and is keyboard/screen-reader accessible.
**Scope:** In `app/sources/page.tsx`, add text labels and appropriate ARIA to the indicator from Task 002 (e.g. visible text "Проверено"/"Пусто"/"Ошибка", and an `aria-live`/`role="status"` region or `aria-label` so the success/empty/error state is announced). Confirm color is never the sole signal. No new components required unless trivially extracted.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Indicator status is discernible without color (text + icon/aria); the state change on check completion is announced to assistive tech; focus/keyboard interaction with the row is unaffected.
**Risk:** low

## Depends On

task-002
