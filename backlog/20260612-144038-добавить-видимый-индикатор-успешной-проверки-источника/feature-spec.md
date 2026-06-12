I now have a clear picture. Key findings:

- The **"Проверить"** button on `/sources` (`app/sources/page.tsx:271`) calls `POST /api/rss/test`, which returns `{ ok, status, itemCount, error, sample }` but **does not persist anything**.
- The only feedback today is a **transient toast** (`OK — N элементов` / `Доступен, но пуст` / `Ошибка: …`), which vanishes after a few seconds (`app/sources/page.tsx:155-157`).
- The `lastStatus` / `lastItemCount` badge on the card (`:251-267`) is only written during a **collect run** (`lib/rss/collect.ts:147-149`), not after a manual test — so a manual check leaves no visible, lasting trace.

---

# Feature Specification

## Summary

On the **Источники** (`/sources`) page, a successful source check ("Проверить") currently produces only a transient toast that disappears after a few seconds and leaves no lasting trace on the source card. This feature adds a **persistent, visible inline indicator of a successful check** directly on each source row — a green "проверено" badge/checkmark showing the result (status, item count, and when it was checked) that remains visible after the toast fades, so users can tell at a glance which sources they have verified and that the verification passed.

## User Stories

- As a user managing sources, I want a lasting visual marker on a source after a successful check so that I don't have to rely on catching the brief toast.
- As a user reviewing my source list, I want to distinguish at a glance sources that passed a check from those that failed, were empty, or were never checked.
- As a user, I want to see *when* a source was last checked and how many items it returned, so I can judge whether the result is still trustworthy.
- As a user, I want the "checking…" → "checked ✓" transition to be obvious on the specific row I clicked, even while other rows are untouched.

## Acceptance Criteria

- [ ] After a check returns a successful result (`ok === true && status === "ok"`), the corresponding source row shows a persistent success indicator (e.g. a green check/badge labeled "Проверено").
- [ ] The success indicator includes the item/post count returned by the check, using the correct unit per source type ("элементов" for RSS, "постов" for telegram/reddit/youtube).
- [ ] The success indicator shows when the check ran (e.g. a relative or short timestamp) so the user knows the result is recent.
- [ ] The indicator persists on the row after the toast disappears and remains until the source is re-checked or the page is reloaded (persistence scope decided in Scope below).
- [ ] An "empty" result (`status === "empty"`) is visually distinct from a success (neutral/info styling, not green).
- [ ] A failed result (`!ok` or error) is visually distinct from a success (error/red styling) and does not show the success indicator.
- [ ] While a check is in progress for a row, that row shows a "Проверка…" state and the success/error indicator for that row is not shown until the result returns.
- [ ] Checking one source does not alter or clear the indicators of other source rows.
- [ ] The indicator is keyboard- and screen-reader-accessible (status conveyed by text/aria, not color alone).
- [ ] The existing toast behavior is preserved (or intentionally complemented), not removed without replacement.

## Scope

- The `/sources` page (`app/sources/page.tsx`) source-list rows and the "Проверить" action.
- Surfacing the result of `POST /api/rss/test` (already returns `ok`, `status`, `itemCount`, `error`, `sample`) as a persistent inline indicator.
- Applies to all current source types (rss, telegram, reddit, youtube) with the correct count unit.
- A decision point to confirm during decomposition: **session-only** indicator (held in React state for the page session) vs. **persisted** indicator (stored on the source so it survives reload). The recommended default is session-only first, as it requires no backend/storage changes; persistence is a follow-up.

## Out of Scope

- Changing the underlying check logic or `/api/rss/test` behavior (fetching, validation, timeouts).
- Automatic/background re-checking or scheduled health monitoring of sources.
- Indicators on other pages (collections, SourcePicker, dashboard) — only `/sources`.
- Reworking the existing `lastStatus`/`lastItemCount` collect-run badge semantics (unless persistence is explicitly chosen, see Scope).
- Showing the sample article titles inline (already returned but not requested here).

## Risks

- **Semantic overlap with `lastStatus`:** the card already renders a `lastStatus`/`lastItemCount` line that is only written by collect runs, not by manual tests. Adding a second status indicator risks confusing users about "last collected" vs "last checked." Decomposition must define how the two coexist (separate labels, or unify).
- **Persistence requires backend work:** if the indicator must survive reload, `/api/rss/test` and storage (`lib/storage/*`, `RssSource` type) need to persist a `lastChecked`/test result — larger change and a migration consideration. Session-only avoids this but the indicator resets on reload.
- **Stale-trust risk:** a green "проверено" badge with no timestamp could imply a source is currently healthy when it was checked long ago; including the check time mitigates this.
- **Color-only signaling** would fail accessibility; must pair color with text/icon/aria.
- **Empty vs success ambiguity:** `status === "empty"` means reachable but no items — must not be shown as a "success" green check.

## Acceptance Scenarios

1. **Successful RSS check leaves a lasting mark**
   - User opens `/sources`, finds an RSS source, clicks **Проверить**.
   - Button shows "Проверка…"; on success a toast "OK — 12 элементов" appears.
   - The row now shows a persistent green "Проверено · 12 элементов · только что" indicator that remains after the toast fades.

2. **Failed check shows no success indicator**
   - User clicks **Проверить** on a broken source.
   - Toast "Ошибка: недоступен" appears; the row shows a red/error indicator and no green "Проверено" badge.

3. **Empty source is distinct from success**
   - User checks a reachable-but-empty feed.
   - Toast "Доступен, но пуст" appears; the row shows a neutral/info indicator, clearly not a green success.

4. **Per-row isolation**
   - User checks Source A (passes) then Source B (passes).
   - Source A keeps its success indicator while Source B is checking; both end with their own correct indicators; neither overwrites the other.

5. **Telegram unit correctness**
   - User checks a Telegram source returning 30 posts.
   - The indicator reads "…30 постов" (not "элементов").

## Manual Verification Scenarios

- Click **Проверить** on a known-good RSS feed; confirm the green success indicator appears and **remains visible** after the toast disappears (~5s).
- Reload the page; confirm the indicator behaves per the chosen persistence decision (gone if session-only, retained if persisted) — and that this matches what the spec/task agreed.
- Check a deliberately invalid URL source; confirm an error indicator, no green badge.
- Check a reachable feed with zero recent items; confirm the "empty/info" styling, not success.
- Check two different sources in quick succession; confirm indicators are independent and not cross-contaminated.
- Inspect with a screen reader / keyboard; confirm the success state is announced via text/aria, not color alone.
- Repeat for each source type (rss, telegram, reddit, youtube) and confirm the count unit label is correct.

## Decomposition Notes

Suggested split into backlog tasks:

1. **UI — inline success indicator (session state):** In `app/sources/page.tsx`, capture each test's result (`ok`, `status`, `itemCount`, `error`, source type) into per-source React state keyed by `source.id`, and render a persistent inline badge on the row (success/empty/error variants, with count, unit, and "checked" time). This is the core, no-backend task that satisfies most acceptance criteria.
2. **Accessibility pass:** ensure the indicator uses text/icon + aria, not color only.
3. **(Optional, gated by Scope decision) Persistence:** extend `POST /api/rss/test` and the `RssSource` storage/type (`lib/storage/*`, `lib/storage/types.ts`) to persist a `lastChecked` timestamp + last-test status, and have the page render from persisted data so the indicator survives reload. Clarify coexistence with the existing collect-run `lastStatus` badge.
4. **Consistency/clarification task:** decide and document how the new "last manual check" indicator and the existing `lastStatus`/`lastItemCount` (collect-run) line are labeled to avoid user confusion.

Recommend implementing task 1 (+2) first as a self-contained, shippable increment; treat task 3 as a follow-up only if reload-persistence is required.

Before decomposition, one product decision should be confirmed: **must the indicator survive a page reload, or is session-only acceptable?** This determines whether backend/storage tasks are in scope.
