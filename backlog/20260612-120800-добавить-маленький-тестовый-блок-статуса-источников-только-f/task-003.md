Status: todo

### Task 003 — `SourceStatusPanel` presentational component

**Goal:** Build a small, self-contained status block that renders aggregated counters and color indication from a `sources` array, independent of any backend change.
**Scope:** New `components/SourceStatusPanel.tsx` taking `sources: RssSource[] | null` as a prop. Compute and display: total, active, and counts by last status — `ok`, `empty`, `error`, and "не проверялись" (no `lastStatus`). Show the freshest `lastFetchedAt` across the set in a human-readable form. Color indication consistent with the list (green=ok, amber/grey=empty, rose/red=error). Handle `sources === null` (shimmer/skeleton matching existing `.shimmer` style) and the empty array (hidden or neutral empty state, no errors). Pure/presentational — no data fetching. `empty` must be counted separately and NOT folded into `error`.
**Suggested files:** `components/SourceStatusPanel.tsx`, `app/sources/page.tsx` (read-only reference for styling/markup conventions), `lib/storage/types.ts` (read-only reference).
**Acceptance criteria:** Maps to AC for the compact block, counter derivation from `lastStatus`/`isActive`, color consistency, empty/loading states, and `empty`-not-an-error semantics. Renders correctly for: mixed-status array, empty array, and `null`.
**Risk:** low

## Depends On

_None_
