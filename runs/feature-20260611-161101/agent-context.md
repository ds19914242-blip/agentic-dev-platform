# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 016 — Finish Sources page remaining English labels

## Planner Input

I have enough to write the plan. The Sources page is mostly translated to Russian already; a handful of labels and the supporting API error messages remain in English.

# Implementation Plan

## Summary

Task 016 finishes the Russian localization of the **Sources** page (`/sources`). The page UI is ~80% translated, but a cluster of form labels, the Telegram time-window options, the editor action buttons, the delete-confirmation modal text, and the Telegram note remain in English. Additionally, the two RSS-sources API routes return English error strings that surface on this page via `toast((await res.json()).error ?? "Ошибка")`. The work is pure UI/string translation — no logic, data-model, or behavior changes.

The other API routes in the affected-files list (`analyze`, `auth/*`, `benchmark`, `favorites/*`, `feedback`, `health/*`) do **not** emit any strings rendered on the Sources page; they are out of scope for this task's stated goal (see Risks).

## Files To Inspect

- `app/sources/page.tsx` — primary file; remaining English labels (confirmed below).
- `app/api/rss/sources/route.ts` — POST error messages surfaced as toasts on save.
- `app/api/rss/sources/[id]/route.ts` — PATCH error messages surfaced as toasts on save/toggle.
- `components/ConfirmModal.tsx` — confirm whether any default labels need overriding (the page passes its own props, so likely no change).
- `lib/storage/types.ts` — `RSS_CATEGORIES` values are data shown verbatim in the category dropdown/badge; confirm these are intentionally left as-is (out of scope, not "labels").

## Implementation Steps

1. **`app/sources/page.tsx` — translate remaining UI labels:**
   - Line 304: `label="Time window"` → `"Период"`.
   - Lines 310–312: option labels `1 day` / `7 days` / `30 days` → `"1 день"` / `"7 дней"` / `"30 дней"`.
   - Lines 317–319: Telegram note "Telegram collection reads only recent public posts…" → Russian equivalent (e.g. «Сбор Telegram читает только недавние публичные посты, а не всю историю канала.»).
   - Line 331: `label="Category"` → `"Категория"`.
   - Line 344: `label="Tags (comma-separated)"` → `"Теги (через запятую)"`.
   - Line 358: `Active` → `"Активен"`.
   - Line 362: `{editingId ? "Save" : "Add source"}` → `{editingId ? "Сохранить" : "Добавить источник"}`.
   - Line 366: `Cancel` → `"Отмена"`.
   - Lines 375–377 (ConfirmModal props): `title="Delete source?"` → `"Удалить источник?"`; `message` "…will be removed." → «Источник «…» будет удалён.»; `confirmLabel="Delete"` → `"Удалить"`.
   - Leave data-driven values untouched: category names from `RSS_CATEGORIES`, `s.category` badge, `lastStatus` ("ok"/"error"), and example placeholders.

2. **`app/api/rss/sources/route.ts` — translate POST error strings** so save-failure toasts render in Russian:
   - "Invalid JSON." → «Некорректный JSON.»
   - "Name is required." → «Укажите название.»
   - "A valid Telegram channel URL or @username is required." → «Укажите корректный URL Telegram-канала или @username.»
   - "RSS URL is required." → «Укажите URL RSS-ленты.»
   - "URL must start with http:// or https://" → «URL должен начинаться с http:// или https://»

3. **`app/api/rss/sources/[id]/route.ts` — translate PATCH error strings** (same phrasings as step 2, plus):
   - "Source not found." → «Источник не найден.»

4. **Consistency check:** ensure new API strings match the wording already used client-side in `page.tsx` (e.g. the page already uses «Укажите URL RSS-ленты» and «URL должен начинаться с http:// или https://») so duplicate validation messages read identically.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- Manual/visual: run the app, open `/sources`; verify the editor form labels, time-window options, Telegram note, action buttons, and the delete modal are all Russ

## plan

I have enough to write the plan. The Sources page is mostly translated to Russian already; a handful of labels and the supporting API error messages remain in English.

# Implementation Plan

## Summary

Task 016 finishes the Russian localization of the **Sources** page (`/sources`). The page UI is ~80% translated, but a cluster of form labels, the Telegram time-window options, the editor action buttons, the delete-confirmation modal text, and the Telegram note remain in English. Additionally, the two RSS-sources API routes return English error strings that surface on this page via `toast((await res.json()).error ?? "Ошибка")`. The work is pure UI/string translation — no logic, data-model, or behavior changes.

The other API routes in the affected-files list (`analyze`, `auth/*`, `benchmark`, `favorites/*`, `feedback`, `health/*`) do **not** emit any strings rendered on the Sources page; they are out of scope for this task's stated goal (see Risks).

## Files To Inspect

- `app/sources/page.tsx` — primary file; remaining English labels (confirmed below).
- `app/api/rss/sources/route.ts` — POST error messages surfaced as toasts on save.
- `app/api/rss/sources/[id]/route.ts` — PATCH error messages surfaced as toasts on save/toggle.
- `components/ConfirmModal.tsx` — confirm whether any default labels need overriding (the page passes its own props, so likely no change).
- `lib/storage/types.ts` — `RSS_CATEGORIES` values are data shown verbatim in the category dropdown/badge; confirm these are intentionally left as-is (out of scope, not "labels").

## Implementation Steps

1. **`app/sources/page.tsx` — translate remaining UI labels:**
   - Line 304: `label="Time window"` → `"Период"`.
   - Lines 310–312: option labels `1 day` / `7 days` / `30 days` → `"1 день"` / `"7 дней"` / `"30 дней"`.
   - Lines 317–319: Telegram note "Telegram collection reads only recent public posts…" → Russian equivalent (e.g. «Сбор Telegram читает только недавние публичные посты, а не всю историю канала.»).
   - Line 331: `label="Category"` → `"Категория"`.
   - Line 344: `label="Tags (comma-separated)"` → `"Теги (через запятую)"`.
   - Line 358: `Active` → `"Активен"`.
   - Line 362: `{editingId ? "Save" : "Add source"}` → `{editingId ? "Сохранить" : "Добавить источник"}`.
   - Line 366: `Cancel` → `"Отмена"`.
   - Lines 375–377 (ConfirmModal props): `title="Delete source?"` → `"Удалить источник?"`; `message` "…will be removed." → «Источник «…» будет удалён.»; `confirmLabel="Delete"` → `"Удалить"`.
   - Leave data-driven values untouched: category names from `RSS_CATEGORIES`, `s.category` badge, `lastStatus` ("ok"/"error"), and example placeholders.

2. **`app/api/rss/sources/route.ts` — translate POST error strings** so save-failure toasts render in Russian:
   - "Invalid JSON." → «Некорректный JSON.»
   - "Name is required." → «Укажите название.»
   - "A valid Telegram channel URL or @username is required." → «Укажите корректный URL Telegram-канала или @username.»
   - "RSS URL is required." → «Укажите URL RSS-ленты.»
   - "URL must start with http:// or https://" → «URL должен начинаться с http:// или https://»

3. **`app/api/rss/sources/[id]/route.ts` — translate PATCH error strings** (same phrasings as step 2, plus):
   - "Source not found." → «Источник не найден.»

4. **Consistency check:** ensure new API strings match the wording already used client-side in `page.tsx` (e.g. the page already uses «Укажите URL RSS-ленты» and «URL должен начинаться с http:// или https://») so duplicate validation messages read identically.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- Manual/visual: run the app, open `/sources`; verify the editor form labels, time-window options, Telegram note, action buttons, and the delete modal are all Russian. Trigger a save with an empty/invalid URL and an invalid Telegram handle to confirm the toast error messages now appear in Ru

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 016 — Finish Sources page remaining English labels

## Based On Plan

I have enough to write the plan. The Sources page is mostly translated to Russian already; a handful of labels and the supporting API error messages remain in English.

# Implementation Plan

## Summary

Task 016 finishes the Russian localization of the **Sources** page (`/sources`). The page UI is ~80% translated, but a cluster of form labels, the Telegram time-window options, the editor action buttons, the delete-confirmation modal text, and the Telegram note remain in English. Additionally, the two RSS-sources API routes return English error strings that surface on this page via `toast((await res.json()).error ?? "Ошибка")`. The work is pure UI/string translation — no logic, data-model, or behavior changes.

The other API routes in the affected-files list (`analyze`, `auth/*`, `benchmark`, `favorites/*`, `feedback`, `health/*`) do **not** emit any strings rendered on the Sources page; they are out of scope for this task's stated goal (see Risks).

## Files To Inspect

- `app/sources/page.tsx` — primary file; remaining English labels (confirmed below).
- `app/api/rss/sources/route.ts` — POST error messages surfaced as toasts on save.
- `app/api/rss/sources/[id]/route.ts` — PATCH error messages surfaced as toasts on save/toggle.
- `components/ConfirmModal.tsx` — confirm whether any default labels need overriding (the page passes its own props, so likely no change).
- `lib/storage/types.ts` — `RSS_CATEGORIES` values are data shown verbatim in the category dropdown/badge; confirm these are intentionally left as-is (out of scope, not "labels").

## Implementation Steps

1. **`app/sources/page.tsx` — translate remaining UI labels:**
   - Line 304: `label="Time window"` → `"Период"`.
   - Lines 310–312: option labels `1 day` / `7 days` / `30 days` → `"1 день"` / `"7 дней"` / `"30 дней"`.
   - Lines 317–319: Telegram note "Telegram collection reads only recent public posts…" → Russian equivalent (e.g. «Сбор Telegram читает только недавние публичные посты, а не всю историю канала.»).
   - Line 331: `label="Category"` → `"Категория"`.
   - Line 344: `label="Tags (comma-separated)"` → `"Теги (через запятую)"`.
   - Line 358: `Active` → `"Активен"`.
   - Line 362: `{editingId ? "Save" : "Add source"}` → `{editingId ? "Сохранить" : "Добавить источник"}`.
   - Line 366: `Cancel` → `"Отмена"`.
   - Lines 375–377 (ConfirmModal props): `title="Delete source?"` → `"Удалить источник?"`; `message` "…will be removed." → «Источник «…» будет удалён.»; `confirmLabel="Delete"` → `"Удалить"`.
   - Leave data-driven values untouched: category names from `RSS_CATEGORIES`, `s.category` badge, `lastStatus` ("ok"/"error"), and example placeholders.

2. **`app/api/rss/sources/route.ts` — translate POST error strings** so save-failure toasts render in Russian:
   - "Invalid JSON." → «Некорректный JSON.»
   - "Name is required." → «Укажите название.»
   - "A valid Telegram channel URL or @username is required." → «Укажите корректный URL Telegram-канала или @username.»
   - "RSS URL is required." → «Укажите URL RSS-ленты.»
   - "URL must start with http:// or https://" → «URL должен начинаться с http:// или https://»

3. **`app/api/rss/sources/[id]/route.ts` — translate PATCH error strings** (same phrasings as step 2, plus):
   - "Source not found." → «Источник не найден.»

4. **Consistency check:** ensure new API strings match the wording already used client-side in `page.tsx` (e.g. the page already uses «Укажите URL RSS-ленты» and «URL должен начинаться с http:// или https://») so duplicate validation messages read identically.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- Manual/visual: run the app, open `/sources`; verify the editor form labels, time-window options, Telegram note, action buttons, and the delete modal are all Russian. Trigger
