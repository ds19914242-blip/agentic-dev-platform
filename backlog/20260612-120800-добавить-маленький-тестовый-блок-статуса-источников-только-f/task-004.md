Status: todo

### Task 004 — Integrate the status block into the Sources page

**Goal:** Mount `SourceStatusPanel` above the source list and wire the test flow so the block reflects live data and persists results.
**Scope:** In `app/sources/page.tsx`: render `SourceStatusPanel` above the list (within the existing `lg:grid-cols-3` layout without breaking it), passing the current `sources` state so it recomputes after each `load()`. Update `test(s)` to send the source `id` to `/api/rss/test` (per Task 001) and call `load()` afterward (already does) so counters and "last checked" time refresh. Ensure `toggleActive` still updates the active counter via `load()`. No new endpoints.
**Suggested files:** `app/sources/page.tsx`.
**Acceptance criteria:** Maps to AC "над списком отображается компактный блок", "обновляются после load()", "время последней проверки … обновляется", and the layout/loading-state criteria. After testing a source, the relevant counter and last-checked time update on reload; toggling active changes the active counter but not the total; layout remains intact at the `lg` breakpoint.
**Risk:** low

## Depends On

_None_
