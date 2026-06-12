PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/60
Run: standard-20260612-144849-690907-96f70c
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 004 — Disambiguate "last manual check" vs collect-run "lastStatus" labels

**Goal:** Prevent user confusion between the new manual-check indicator and the existing collect-run `lastStatus`/`lastItemCount` line, which currently reads "последний: …".
**Scope:** In `app/sources/page.tsx`, adjust labels so the two lines are clearly distinct (e.g. existing collect line → "последний сбор: …"; new manual-check badge → "Проверено …"). Documentation/comment of the distinction. No change to collect-run semantics or data.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** The collect-run status line and the new manual-check indicator have visually/textually distinct labels so a user can tell "last collected" from "last checked"; no change to `lastStatus`/`lastItemCount` data flow.
**Risk:** low

## Depends On

_None_
