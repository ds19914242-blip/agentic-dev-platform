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

### Task 004 — Disambiguate "last manual check" vs collect-run "lastStatus" labels

**Goal:** Prevent user confusion between the new manual-check indicator and the existing collect-run `lastStatus`/`lastItemCount` line, which currently reads "последний: …".
**Scope:** In `app/sources/page.tsx`, adjust labels so the two lines are clearly distinct (e.g. existing collect line → "последний сбор: …"; new manual-check badge → "Проверено …"). Documentation/comment of the distinction. No change to collect-run semantics or data.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** The collect-run status line and the new manual-check indicator have visually/textually distinct labels so a user can tell "last collected" from "last checked"; no change to `lastStatus`/`lastItemCount` data flow.
**Risk:** low

## Depends On

_None_

