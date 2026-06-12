# Epic

## Summary

On the **Источники** (`/sources`) page, clicking **Проверить** currently shows only a transient toast that disappears after a few seconds and leaves no lasting trace on the source card. This epic adds a **persistent, accessible, per-row indicator of the last manual check** — a green "Проверено" success badge (with count, correct unit, and check time), distinct neutral styling for empty results, and distinct error styling for failures.

The default approach is **session-only** state (React state keyed by `source.id`), which satisfies all core acceptance criteria with no backend changes. Reload-persistence is split into an explicitly gated follow-up task. The existing `lastStatus`/`lastItemCount` collect-run line is preserved and disambiguated by label.

Findings confirming scope:
- `test()` (`app/sources/page.tsx:132-162`) already receives `{ ok, status, itemCount, error, sample }` from `POST /api/rss/test` but discards it into a transient toast.
- The card's existing status line (`:251-267`) is written only by collect runs (`lastStatus`/`lastItemCount`), not by manual tests.
- Source types and the unit decision (`элементов` vs `постов`) already exist locally (`:154`); `RssSource`/`SourceType` live in `lib/storage/types.ts`.

## Task List

### Task 001 — Capture manual-check result into per-source session state

**Goal:** Stop discarding the `/api/rss/test` response. Store each row's last manual-check result in React state keyed by `source.id`, alongside the existing toast.
**Scope:** In `app/sources/page.tsx`, add a state map (e.g. `checkResults: Record<string, { status: "ok" | "empty" | "error"; itemCount?: number; error?: string; sourceType: SourceType; checkedAt: number }>`). In `test()`, after parsing `r`, write the result for `s.id` into that map (success, empty, and error branches) while keeping the existing toast calls unchanged. Do not yet render anything new. Ensure per-row isolation: writing one source's result must not touch other entries. Clear/replace only the clicked row's entry at the start of a re-check.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Result object (status, itemCount, error, sourceType, checkedAt) is recorded per `source.id` for all three outcome branches; existing toast behavior preserved; checking one source leaves other entries in the map untouched.
**Risk:** low

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

### Task 003 — Accessibility pass on the indicator

**Goal:** Ensure the check indicator conveys status via text/aria/icon, not color alone, and is keyboard/screen-reader accessible.
**Scope:** In `app/sources/page.tsx`, add text labels and appropriate ARIA to the indicator from Task 002 (e.g. visible text "Проверено"/"Пусто"/"Ошибка", and an `aria-live`/`role="status"` region or `aria-label` so the success/empty/error state is announced). Confirm color is never the sole signal. No new components required unless trivially extracted.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** Indicator status is discernible without color (text + icon/aria); the state change on check completion is announced to assistive tech; focus/keyboard interaction with the row is unaffected.
**Risk:** low

### Task 004 — Disambiguate "last manual check" vs collect-run "lastStatus" labels

**Goal:** Prevent user confusion between the new manual-check indicator and the existing collect-run `lastStatus`/`lastItemCount` line, which currently reads "последний: …".
**Scope:** In `app/sources/page.tsx`, adjust labels so the two lines are clearly distinct (e.g. existing collect line → "последний сбор: …"; new manual-check badge → "Проверено …"). Documentation/comment of the distinction. No change to collect-run semantics or data.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** The collect-run status line and the new manual-check indicator have visually/textually distinct labels so a user can tell "last collected" from "last checked"; no change to `lastStatus`/`lastItemCount` data flow.
**Risk:** low

### Task 005 — (Optional, gated by Scope decision) Persist last manual-check result across reload

**Goal:** Only if the product decision requires the indicator to survive a page reload: persist a manual-check timestamp + status so the indicator renders from stored data.
**Scope:** Extend `POST /api/rss/test` to persist a last-test result (e.g. `lastChecked` timestamp + `lastTestStatus`/`lastTestItemCount`) onto the source via `RssSourceStorage.update`; add the fields to `RssSource` in `lib/storage/types.ts` (and any local storage implementation under `lib/storage/*`); have `app/sources/page.tsx` hydrate the indicator from persisted source data on load, falling back to/merging with session state. Keep these fields separate from collect-run `lastStatus`/`lastItemCount` to preserve the Task 004 distinction. Consider back-compat for existing sources (fields optional).
**Suggested files:** `app/api/rss/test/route.ts`, `lib/storage/types.ts`, `lib/storage/*` (local implementation), `app/sources/page.tsx`
**Acceptance criteria:** A successful/empty/error manual check is persisted on the source and the corresponding indicator survives a page reload; new fields are optional and do not break existing sources; collect-run `lastStatus`/`lastItemCount` semantics unchanged; coexistence labeling from Task 004 maintained.
**Risk:** medium

## Depends On

- **Task 001** — _None_
- **Task 002** — task-001
- **Task 003** — task-002
- **Task 004** — _None_
- **Task 005** — task-002

---

**Note (product decision to confirm before Task 005):** The spec leaves one open decision — *must the indicator survive a page reload, or is session-only acceptable?* Tasks 001–004 deliver a complete, shippable session-only increment. Task 005 is a gated follow-up that should only be scheduled if reload-persistence is explicitly required.
