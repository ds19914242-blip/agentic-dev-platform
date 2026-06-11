# Implementation Plan

## Summary

Task 007 translates the **Collections page** UI from English to Russian, matching the established pattern from Tasks 001/003/004/006 (translate only user-facing strings in the page component; leave logic, classNames, hrefs, and API contracts untouched). The only file with translatable UI is `app/collections/page.tsx`. The other listed files (`app/rss/collections/page.tsx` and the `app/api/**` routes) contain no user-facing page copy — the rss/collections page is a bare redirect, and the API routes are backend handlers. They are in scope only as optional secondary surfaces (API `error` strings surfaced via toast).

## Files To Inspect

- `app/collections/page.tsx` — **primary target.** All visible English strings: headings, descriptions, buttons, placeholders, empty states, toasts, confirm modal copy, and the `Pane`/`Empty`/`SourceRow` helper strings.
- `app/rss/collections/page.tsx` — redirect-only (`redirect("/collections")`); **no changes needed**.
- `app/api/rss/collections/route.ts` and `app/api/rss/collections/[id]/route.ts` — check whether `error` response strings (surfaced by `toast((await res.json()).error ?? "Failed")`) should also be translated; prior tasks left API strings in English, so default is **no change**.
- Reference: `app/dashboard/page.tsx` (commit `51eb9ef`) for tone/terminology — e.g. "Collection" → «коллекция», "Source" → «источник», "Analyze" → «Анализировать».

## Implementation Steps

1. In `app/collections/page.tsx`, translate the following literal strings to Russian, preserving surrounding JSX, emojis (`+`, `▶`, `×`), and the existing `toLocaleDateString("ru-RU")`:
   - Header: `Collections` → `Коллекции`; subtitle `Group sources and run analysis directly from a collection.`
   - Button `+ New collection`; card empty state `No collections yet. Create one to start collecting RSS / Telegram sources.`
   - Card meta: `{n} sources · updated` → `{n} источников · обновлено` (keep the `{c.sourceIds.length}` and date interpolation).
   - Buttons: `Opening…`, `▶ Analyze`, `Edit`, `Delete`.
   - Editor: `Edit collection` / `New collection`; placeholders `Collection name (e.g. AI Daily)` and `Description`; pane titles `Available (…)` / `In collection (…)`; empty panes `All sources added (or none exist yet).` / `Click sources on the left to add them.`; buttons `Save collection` / `Create collection` / `Cancel`.
   - Toasts: `Name is required`, `Failed`, `Collection updated`, `Collection created`, `Collection deleted`.
   - `ConfirmModal`: `title="Delete collection?"`, `message` `«{name}» will be removed (sources are not deleted).`, `confirmLabel="Delete"`.
2. Keep the dynamic pane titles as template literals (e.g. `` `Доступные (${available.length})` ``).
3. Leave the `"telegram"`/`"rss"` source-type labels (`Telegram`, `RSS`) as-is (proper nouns), matching prior tasks.
4. Do **not** alter `app/rss/collections/page.tsx` or any API route unless a follow-up explicitly requests translating API error strings.

## Validation Steps

- `npx tsc --noEmit` (or `npm run build`) — confirm no type/JSX breakage from edited strings.
- `npm run lint` if configured.
- Visual/manual: load `/collections`, exercise create/edit/delete and the analyze button to confirm all copy renders in Russian and no untranslated strings remain.
- `git diff app/collections/page.tsx` — verify only string literals changed (no logic, classNames, or hrefs touched).

## Risks

- **Scope creep:** the affected-files list is broad, but only `app/collections/page.tsx` has page copy. Translating API routes would diverge from the established Task 001/003/004/006 pattern (UI-only) — confirm before touching backend strings.
- **Missed strings:** ensure helper components (`Pane`, `Empty`, `SourceRow`) and the toast/error fallbacks are included — easy to overlook below the main `return`.
- **Encoding/quotes:** preserve the existing guillemets (`«»`) in the confirm message and avoid breaking template-literal interpolation.
- **Terminology consistency:** reuse the dashboard's choices (Коллекция, Источник, Анализировать) so cross-page navigation reads consistently.
