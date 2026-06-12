# Standard Task Execution

You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: implementation_task
Pipeline: standard
Risk: low
Status: in_progress

### Task 003 — Accessibility pass on the indicator

**Goal:** Ensure the check indicator conveys status via text/aria/icon, not color alone, and is keyboard/screen-reader accessible.
**Scope:** In `app/sources/page.tsx`, add text labels and appropriate ARIA to the indicator from Task 002 (e.g. visible text "Проверено"/"Пусто"/"Ошибка", and an `aria-live`/`role="status"` region or `aria-label` so the success/empty/error state is announced). Confirm color is never the sole signal. No new components required unless trivially extracted.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Indicator status is discernible without color (text + icon/aria); the state change on check completion is announced to assistive tech; focus/keyboard interaction with the row is unaffected.
**Risk:** low

## Depends On

_None_

