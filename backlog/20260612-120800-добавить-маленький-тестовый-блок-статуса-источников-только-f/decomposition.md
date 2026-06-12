# Epic

## Summary

Add a small "source health" status block to the Sources page (`app/sources/page.tsx`) that aggregates the last-check state of all RSS/Telegram/Reddit sources: total, active, and per-status counts (`ok` / `empty` / `error` / not-yet-checked), plus the freshest "last checked" time. The `RssSource` type already declares `lastStatus` / `lastItemCount` / `lastError` / `lastFetchedAt`, the list row already renders `lastStatus`, but `/api/rss/test` never persists results — so today status is per-toast only. This epic wires test results into storage and surfaces an aggregated, persistent overview.

The decomposition keeps the UI block buildable in parallel with the backend persistence work (the UI aggregates from already-loaded `sources` and degrades gracefully when fields are empty), and isolates the storage race-condition hardening so it can land independently.

## Task List

### Task 001 — Persist test results into the source record

**Goal:** Make pressing «Проверить» durable — `POST /api/rss/test` records `lastStatus`, `lastItemCount`, `lastError`, `lastFetchedAt` onto the tested source so the status survives a page reload.
**Scope:** Extend `POST /api/rss/test` to accept an optional source `id` in the request body (chosen fork from Decomposition Note 1 — keep one round-trip rather than a separate client PATCH). After computing the fetch result for all three branches (rss/telegram/reddit), when `id` is present and resolves to an existing source, call `rssSourceStorage.update(id, {...})` with the four status fields (`lastStatus` from `res.status`, `lastItemCount` from `res.itemCount`, `lastError` from `res.error` or undefined on success, `lastFetchedAt` = now ISO). The test response shape stays the same; persistence is best-effort and must never throw or change the HTTP status. Do not expand what error text is stored beyond what the list already shows. No schema change.
**Suggested files:** `app/api/rss/test/route.ts`, `lib/storage/rss.ts` (read-only reference), `lib/storage/types.ts` (read-only reference).
**Acceptance criteria:** Maps to AC "результат … сохраняется в хранилище и виден после перезагрузки" and "Никакие чувствительные данные … не раскрываются". After a test of a working RSS source, the stored source has `lastStatus="ok"` and a fresh `lastFetchedAt`; a broken URL stores `lastStatus="error"` with `lastError`; an empty-but-reachable source stores `lastStatus="empty"` (not error). Calling `/api/rss/test` without an `id` behaves exactly as today.
**Risk:** medium

### Task 002 — Serialize source-storage writes to prevent lost updates

**Goal:** Harden `LocalRssSourceStorage` so concurrent `update` calls (e.g. several sources tested in quick succession, each a read-modify-write over one JSON file) cannot clobber each other.
**Scope:** Add an in-process write serialization (e.g. a promise chain / mutex) around the read-modify-write in `LocalRssSourceStorage.update` (and other mutating methods that read-then-write the same file) so operations queue rather than interleave. No public API or return-shape change; same method signatures.
**Suggested files:** `lib/storage/rss.ts`.
**Acceptance criteria:** Maps to Risk "Гонки при параллельных проверках … могут терять записи". Firing multiple overlapping `update` calls on different source ids results in all updates persisted (none lost). Existing list/get/create/delete behavior unchanged.
**Risk:** medium

### Task 003 — `SourceStatusPanel` presentational component

**Goal:** Build a small, self-contained status block that renders aggregated counters and color indication from a `sources` array, independent of any backend change.
**Scope:** New `components/SourceStatusPanel.tsx` taking `sources: RssSource[] | null` as a prop. Compute and display: total, active, and counts by last status — `ok`, `empty`, `error`, and "не проверялись" (no `lastStatus`). Show the freshest `lastFetchedAt` across the set in a human-readable form. Color indication consistent with the list (green=ok, amber/grey=empty, rose/red=error). Handle `sources === null` (shimmer/skeleton matching existing `.shimmer` style) and the empty array (hidden or neutral empty state, no errors). Pure/presentational — no data fetching. `empty` must be counted separately and NOT folded into `error`.
**Suggested files:** `components/SourceStatusPanel.tsx`, `app/sources/page.tsx` (read-only reference for styling/markup conventions), `lib/storage/types.ts` (read-only reference).
**Acceptance criteria:** Maps to AC for the compact block, counter derivation from `lastStatus`/`isActive`, color consistency, empty/loading states, and `empty`-not-an-error semantics. Renders correctly for: mixed-status array, empty array, and `null`.
**Risk:** low

### Task 004 — Integrate the status block into the Sources page

**Goal:** Mount `SourceStatusPanel` above the source list and wire the test flow so the block reflects live data and persists results.
**Scope:** In `app/sources/page.tsx`: render `SourceStatusPanel` above the list (within the existing `lg:grid-cols-3` layout without breaking it), passing the current `sources` state so it recomputes after each `load()`. Update `test(s)` to send the source `id` to `/api/rss/test` (per Task 001) and call `load()` afterward (already does) so counters and "last checked" time refresh. Ensure `toggleActive` still updates the active counter via `load()`. No new endpoints.
**Suggested files:** `app/sources/page.tsx`.
**Acceptance criteria:** Maps to AC "над списком отображается компактный блок", "обновляются после load()", "время последней проверки … обновляется", and the layout/loading-state criteria. After testing a source, the relevant counter and last-checked time update on reload; toggling active changes the active counter but not the total; layout remains intact at the `lg` breakpoint.
**Risk:** low

### Task 005 — (Optional) «Проверить все активные» action

**Goal:** Add a one-click run that sequentially (or bounded-parallel) tests all active sources and refreshes the summary.
**Scope:** Button near the status block that iterates active sources, calls the test+persist flow for each with limited concurrency to avoid storage races, shows progress/disabled state, then `load()`s once. Explicitly Out of Scope for the core feature — implement only as a follow-up.
**Suggested files:** `app/sources/page.tsx`, `components/SourceStatusPanel.tsx`.
**Acceptance criteria:** Maps to the optional user story "одним действием запустить проверку всех активных источников". Clicking the action updates every active source's stored status and the block reflects the new aggregate.
**Risk:** medium

### Task 006 — QA pass and aggregation unit test

**Goal:** Validate the manual scenarios and lock the aggregation logic with a lightweight test.
**Scope:** Execute the spec's Manual Verification Scenarios (mixed types, ok/error/empty persistence + reload, toggle active, no-sources, slow-network skeleton, last-checked refresh). Add a small component/unit test for the counter aggregation in `SourceStatusPanel` (status bucketing incl. `empty`≠`error` and not-checked) if a test setup exists.
**Suggested files:** test file alongside `components/SourceStatusPanel.tsx` (per repo test conventions), `app/sources/page.tsx` (read-only reference).
**Acceptance criteria:** Maps to "Manual Verification Scenarios" and the "лёгкий компонентный тест агрегации" note. All listed scenarios pass; aggregation test covers ok/empty/error/not-checked and active vs total.
**Risk:** low

## Depends On

- Task 001 → task-002
- Task 002 → _None_
- Task 003 → _None_
- Task 004 → task-001, task-003
- Task 005 → task-004
- Task 006 → task-003, task-004

_Note: per-task `## Depends On` sections, as required:_

**Task 001 Depends On:** task-002
**Task 002 Depends On:** _None_
**Task 003 Depends On:** _None_
**Task 004 Depends On:** task-001, task-003
**Task 005 Depends On:** task-004
**Task 006 Depends On:** task-003, task-004
