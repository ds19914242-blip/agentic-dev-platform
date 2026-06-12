PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/59
Run: standard-20260612-144547-889657-be7ff4
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 002 — Render persistent inline check indicator (success / empty / error variants)

**Goal:** Render a persistent inline badge on each source row from the session state captured in Task 001, with success/empty/error variants, count + correct unit, and a check timestamp.
**Scope:** In `app/sources/page.tsx`, in the row block near the existing status line (`:245-268`), render a badge when a check result exists for `s.id`:
- Success (`ok === true && status === "ok"`): green "Проверено" badge including `itemCount` + unit (`элементов` for `rss`, `постов` for `telegram`/`reddit`/`youtube`) + check time (relative/short, e.g. "только что").
- Empty (`status === "empty"`): neutral/info styling, clearly not green; no success checkmark.
- Error (`!ok` or error): red/error styling; no success badge.
While `testing === s.id`, show the in-progress "Проверка…" state for that row and suppress its success/error indicator until the result returns (the button already shows "Проверка…" at `:271-273`). Keep the existing `lastStatus`/`lastItemCount` line intact. Reuse the existing unit logic (`:154`).
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Maps to acceptance criteria — success badge with count+unit+time persists after toast fades; empty visually distinct (not green); error visually distinct, no success badge; in-progress row shows "Проверка…" and hides its indicator until result; other rows' indicators unaffected; success requires `ok === true && status === "ok"`.
**Risk:** low

## Depends On

task-001
