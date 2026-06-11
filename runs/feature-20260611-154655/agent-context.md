# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 007 — Translate Collections page

## Planner Input

# Implementation Plan

## Summary

Translate the visible UI text of the Collections page to Russian. The only file with rendered UI is `app/collections/page.tsx`; `app/rss/collections/page.tsx` is a pure server redirect with no UI. Following the established pattern from prior translation tasks (e.g. the reports page, commit `f12d042`), the change is limited to the page component's user-facing strings — no logic, props, class names, or API contracts change. The many API routes listed in "Affected Files" contain only `error` JSON payloads and are not part of the visible page UI; they are out of scope (consistent with prior tasks that touched only the page file).

## Files To Inspect

- `app/collections/page.tsx` — primary target; contains all rendered strings, placeholders, button labels, toast messages, and the confirm modal text.
- `app/rss/collections/page.tsx` — confirmed redirect-only (`redirect("/collections")`); no changes needed.
- `components/ConfirmModal.tsx` — verify it renders the `title`/`message`/`confirmLabel` props passed in (so translating the props is sufficient).
- `components/Toast.tsx` — verify `toast(message, variant)` renders the message string verbatim.
- A prior translated page (`app/reports/page.tsx`) — to match tone, formality, and string-only diff scope.

## Implementation Steps

Edit only `app/collections/page.tsx`, replacing the following English strings with Russian (keep all JSX structure, variables, and interpolations intact):

1. **Header** (lines 99–106): `Collections` → e.g. «Коллекции»; subtitle `Group sources and run analysis directly from a collection.`; button `+ New collection`.
2. **Empty / loading states** (line 113): `No collections yet. Create one to start collecting RSS / Telegram sources.`
3. **Card meta** (lines 122–130): `{n} sources · updated …` (translate `sources`/`updated`, keep the count and `toLocaleDateString("ru-RU")`); `Opening…` and `▶ Analyze` button labels.
4. **Card actions** (lines 133–141): `Edit`, `Delete`.
5. **Editor heading** (lines 151–153): `Edit collection` / `New collection`.
6. **Inputs** (lines 158, 164): placeholders `Collection name (e.g. AI Daily)`, `Description`.
7. **Panes & empties** (lines 170–186): `Available (n)` → «Доступные (n)», `In collection (n)`, `All sources added (or none exist yet).`, `Click sources on the left to add them.`
8. **Editor buttons** (lines 192–195): `Save collection` / `Create collection`, `Cancel`.
9. **Confirm modal** (lines 203–205): `title` `Delete collection?`, `message` `«{name}» will be removed (sources are not deleted).` (preserve the `pendingDelete?.name` interpolation), `confirmLabel` `Delete`.
10. **Toast messages** (lines 53, 66–67, 88): `Name is required`, `Failed`, `Collection updated` / `Collection created`, `Collection deleted`.
11. **SourceRow subtitle** (line 241): keep `Telegram` / `RSS` labels as-is (proper nouns); these are conventionally untranslated.

Leave the fallback `(await res.json()).error ?? "Failed"` — translate the `"Failed"` fallback; the API-supplied `error` text is out of scope.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck script) — confirm no type errors introduced.
- Run the lint/build if configured (`npm run lint` / `npm run build`).
- Manually load `/collections`: verify header, new/edit editor, available/included panes, analyze/edit/delete buttons, toasts, and the delete confirmation modal all render in Russian with correct interpolated counts/names.
- Verify `/rss/collections` still redirects to `/collections`.
- `git diff --stat` should show only `app/collections/page.tsx` changed.

## Risks

- **Scope creep**: API route `error` strings are tempting but were excluded in prior tasks; including them widens the diff and risks contract assumptions. Keep to the page file unless the task explicitly wants error messages translated.
- **Interpolation breakage**: 

## plan

# Implementation Plan

## Summary

Translate the visible UI text of the Collections page to Russian. The only file with rendered UI is `app/collections/page.tsx`; `app/rss/collections/page.tsx` is a pure server redirect with no UI. Following the established pattern from prior translation tasks (e.g. the reports page, commit `f12d042`), the change is limited to the page component's user-facing strings — no logic, props, class names, or API contracts change. The many API routes listed in "Affected Files" contain only `error` JSON payloads and are not part of the visible page UI; they are out of scope (consistent with prior tasks that touched only the page file).

## Files To Inspect

- `app/collections/page.tsx` — primary target; contains all rendered strings, placeholders, button labels, toast messages, and the confirm modal text.
- `app/rss/collections/page.tsx` — confirmed redirect-only (`redirect("/collections")`); no changes needed.
- `components/ConfirmModal.tsx` — verify it renders the `title`/`message`/`confirmLabel` props passed in (so translating the props is sufficient).
- `components/Toast.tsx` — verify `toast(message, variant)` renders the message string verbatim.
- A prior translated page (`app/reports/page.tsx`) — to match tone, formality, and string-only diff scope.

## Implementation Steps

Edit only `app/collections/page.tsx`, replacing the following English strings with Russian (keep all JSX structure, variables, and interpolations intact):

1. **Header** (lines 99–106): `Collections` → e.g. «Коллекции»; subtitle `Group sources and run analysis directly from a collection.`; button `+ New collection`.
2. **Empty / loading states** (line 113): `No collections yet. Create one to start collecting RSS / Telegram sources.`
3. **Card meta** (lines 122–130): `{n} sources · updated …` (translate `sources`/`updated`, keep the count and `toLocaleDateString("ru-RU")`); `Opening…` and `▶ Analyze` button labels.
4. **Card actions** (lines 133–141): `Edit`, `Delete`.
5. **Editor heading** (lines 151–153): `Edit collection` / `New collection`.
6. **Inputs** (lines 158, 164): placeholders `Collection name (e.g. AI Daily)`, `Description`.
7. **Panes & empties** (lines 170–186): `Available (n)` → «Доступные (n)», `In collection (n)`, `All sources added (or none exist yet).`, `Click sources on the left to add them.`
8. **Editor buttons** (lines 192–195): `Save collection` / `Create collection`, `Cancel`.
9. **Confirm modal** (lines 203–205): `title` `Delete collection?`, `message` `«{name}» will be removed (sources are not deleted).` (preserve the `pendingDelete?.name` interpolation), `confirmLabel` `Delete`.
10. **Toast messages** (lines 53, 66–67, 88): `Name is required`, `Failed`, `Collection updated` / `Collection created`, `Collection deleted`.
11. **SourceRow subtitle** (line 241): keep `Telegram` / `RSS` labels as-is (proper nouns); these are conventionally untranslated.

Leave the fallback `(await res.json()).error ?? "Failed"` — translate the `"Failed"` fallback; the API-supplied `error` text is out of scope.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck script) — confirm no type errors introduced.
- Run the lint/build if configured (`npm run lint` / `npm run build`).
- Manually load `/collections`: verify header, new/edit editor, available/included panes, analyze/edit/delete buttons, toasts, and the delete confirmation modal all render in Russian with correct interpolated counts/names.
- Verify `/rss/collections` still redirects to `/collections`.
- `git diff --stat` should show only `app/collections/page.tsx` changed.

## Risks

- **Scope creep**: API route `error` strings are tempting but were excluded in prior tasks; including them widens the diff and risks contract assumptions. Keep to the page file unless the task explicitly wants error messages translated.
- **Interpolation breakage**: strings mix variables (`${available.length}`, `pendingDelete?.name`, date formatting). Edits must preserve temp

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 007 — Translate Collections page

## Based On Plan

# Implementation Plan

## Summary

Translate the visible UI text of the Collections page to Russian. The only file with rendered UI is `app/collections/page.tsx`; `app/rss/collections/page.tsx` is a pure server redirect with no UI. Following the established pattern from prior translation tasks (e.g. the reports page, commit `f12d042`), the change is limited to the page component's user-facing strings — no logic, props, class names, or API contracts change. The many API routes listed in "Affected Files" contain only `error` JSON payloads and are not part of the visible page UI; they are out of scope (consistent with prior tasks that touched only the page file).

## Files To Inspect

- `app/collections/page.tsx` — primary target; contains all rendered strings, placeholders, button labels, toast messages, and the confirm modal text.
- `app/rss/collections/page.tsx` — confirmed redirect-only (`redirect("/collections")`); no changes needed.
- `components/ConfirmModal.tsx` — verify it renders the `title`/`message`/`confirmLabel` props passed in (so translating the props is sufficient).
- `components/Toast.tsx` — verify `toast(message, variant)` renders the message string verbatim.
- A prior translated page (`app/reports/page.tsx`) — to match tone, formality, and string-only diff scope.

## Implementation Steps

Edit only `app/collections/page.tsx`, replacing the following English strings with Russian (keep all JSX structure, variables, and interpolations intact):

1. **Header** (lines 99–106): `Collections` → e.g. «Коллекции»; subtitle `Group sources and run analysis directly from a collection.`; button `+ New collection`.
2. **Empty / loading states** (line 113): `No collections yet. Create one to start collecting RSS / Telegram sources.`
3. **Card meta** (lines 122–130): `{n} sources · updated …` (translate `sources`/`updated`, keep the count and `toLocaleDateString("ru-RU")`); `Opening…` and `▶ Analyze` button labels.
4. **Card actions** (lines 133–141): `Edit`, `Delete`.
5. **Editor heading** (lines 151–153): `Edit collection` / `New collection`.
6. **Inputs** (lines 158, 164): placeholders `Collection name (e.g. AI Daily)`, `Description`.
7. **Panes & empties** (lines 170–186): `Available (n)` → «Доступные (n)», `In collection (n)`, `All sources added (or none exist yet).`, `Click sources on the left to add them.`
8. **Editor buttons** (lines 192–195): `Save collection` / `Create collection`, `Cancel`.
9. **Confirm modal** (lines 203–205): `title` `Delete collection?`, `message` `«{name}» will be removed (sources are not deleted).` (preserve the `pendingDelete?.name` interpolation), `confirmLabel` `Delete`.
10. **Toast messages** (lines 53, 66–67, 88): `Name is required`, `Failed`, `Collection updated` / `Collection created`, `Collection deleted`.
11. **SourceRow subtitle** (line 241): keep `Telegram` / `RSS` labels as-is (proper nouns); these are conventionally untranslated.

Leave the fallback `(await res.json()).error ?? "Failed"` — translate the `"Failed"` fallback; the API-supplied `error` text is out of scope.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck script) — confirm no type errors introduced.
- Run the lint/build if configured (`npm run lint` / `npm run build`).
- Manually load `/collections`: verify header, new/edit editor, available/included panes, analyze/edit/delete buttons, toasts, and the delete confirmation modal all render in Russian with correct interpolated counts/names.
- Verify `/rss/collections` still redirects to `/collections`.
- `git diff --stat` should show only `app/collections/page.tsx` changed.

## Risks

- **Scope creep**: API route `error` strings are tempting but were excluded in prior tasks; including them widens the diff and risks contract assumptions. Keep to the page file unless the task explicitly wants error messages translated.
- **Interpolation breakage**: strings mix 
