PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/58
Run: standard-20260612-144546-462568-29d0cc
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 001 — Capture manual-check result into per-source session state

**Goal:** Stop discarding the `/api/rss/test` response. Store each row's last manual-check result in React state keyed by `source.id`, alongside the existing toast.
**Scope:** In `app/sources/page.tsx`, add a state map (e.g. `checkResults: Record<string, { status: "ok" | "empty" | "error"; itemCount?: number; error?: string; sourceType: SourceType; checkedAt: number }>`). In `test()`, after parsing `r`, write the result for `s.id` into that map (success, empty, and error branches) while keeping the existing toast calls unchanged. Do not yet render anything new. Ensure per-row isolation: writing one source's result must not touch other entries. Clear/replace only the clicked row's entry at the start of a re-check.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Result object (status, itemCount, error, sourceType, checkedAt) is recorded per `source.id` for all three outcome branches; existing toast behavior preserved; checking one source leaves other entries in the map untouched.
**Risk:** low

## Depends On

_None_
