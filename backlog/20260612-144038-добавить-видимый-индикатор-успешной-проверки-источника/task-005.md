Type: feature_task
Pipeline: full
Risk: medium
Status: no_changes_needed

### Task 005 — (Optional, gated by Scope decision) Persist last manual-check result across reload

**Goal:** Only if the product decision requires the indicator to survive a page reload: persist a manual-check timestamp + status so the indicator renders from stored data.
**Scope:** Extend `POST /api/rss/test` to persist a last-test result (e.g. `lastChecked` timestamp + `lastTestStatus`/`lastTestItemCount`) onto the source via `RssSourceStorage.update`; add the fields to `RssSource` in `lib/storage/types.ts` (and any local storage implementation under `lib/storage/*`); have `app/sources/page.tsx` hydrate the indicator from persisted source data on load, falling back to/merging with session state. Keep these fields separate from collect-run `lastStatus`/`lastItemCount` to preserve the Task 004 distinction. Consider back-compat for existing sources (fields optional).
**Suggested files:** `app/api/rss/test/route.ts`, `lib/storage/types.ts`, `lib/storage/*` (local implementation), `app/sources/page.tsx`
**Acceptance criteria:** A successful/empty/error manual check is persisted on the source and the corresponding indicator survives a page reload; new fields are optional and do not break existing sources; collect-run `lastStatus`/`lastItemCount` semantics unchanged; coexistence labeling from Task 004 maintained.
**Risk:** medium

## Depends On

task-002
