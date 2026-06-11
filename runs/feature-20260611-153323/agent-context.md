# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 017 — Finish Profiles page remaining English labels

## Planner Input

# Implementation Plan

## Summary

Task 017 finishes the Russian localization of the **Profiles page**. The page (`app/profiles/page.tsx`) is ~90% translated, but a handful of hardcoded English labels remain in the UI, and the supporting API routes plus built-in profile data still emit English. The work is purely string replacement (EN→RU) of **user-visible** text — no logic, schema, or behavior changes. The login route already uses Russian error strings (`"Неверный логин или пароль."`), establishing the convention to follow for the other routes.

## Files To Inspect

Already inspected (findings below):
- `app/profiles/page.tsx` — main page; remaining English labels here.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` shown in the list (English).
- `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts` — `error` JSON strings + `"Untitled"` default name.
- `app/api/analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`, `health/db` routes — `error`/`note` JSON strings.

Worth a quick cross-check (not in scope to edit, but to keep terminology consistent):
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — topic chips render verbatim; decide whether topics are intentionally left in English.
- `components/Toast.tsx` / `components/ConfirmModal.tsx` — confirm toasts already pass Russian; no change needed.

## Implementation Steps

1. **`app/profiles/page.tsx` — remaining visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders raw `fast/balanced/deep` — map to a Russian label (e.g. `Быстрый/Сбалансированный/Глубокий`) via a small lookup, matching the select options below.
   - Line 192: `label="Include keywords"` → `Ключевые слова (включить)`.
   - Line 206: `label="Exclude keywords"` → `Ключевые слова (исключить)`.
   - Lines 234–236: `<option>` labels `Fast`/`Balanced`/`Deep` → Russian (keep `value` attributes `fast`/`balanced`/`deep` unchanged — they are sent to the API).
   - Confirm the placeholder `"добавить…"` (line 299) and all other strings are already Russian (they are).

2. **`src/analysis/profiles.ts` — built-in profile copy:** translate each `description` to Russian. Decide on `name`: these read as product/segment proper nouns (e.g. "AI Security", "IAM Market") — recommend keeping names but translating descriptions, OR translate both for full consistency (see Risks/decision). Do **not** change `id`, `selectedTopics`, or keyword values (those feed matching logic and are domain terms).

3. **`app/api/profiles/route.ts`:** translate the `"Invalid JSON."` error string; translate `"Untitled"` default name → `"Без названия"`.

4. **`app/api/profiles/[id]/route.ts`:** translate `"Profile not found."`, `"Built-in profiles cannot be edited."`, `"Invalid JSON."`, `"Built-in profiles cannot be deleted."`.

5. **Remaining affected API routes** — translate only user-facing `error`/`note` strings to Russian, leaving keys, status codes, and env-var names intact:
   - `analyze`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
   - `benchmark`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
   - `auth/login`: `"Server auth is not configured."`, `"Invalid request."` (note `"Неверный логин или пароль."` is already RU).
   - `auth/logout`: no user-facing strings — no change.
   - `favorites` / `favorites/[id]`: `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
   - `feedback`: `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
   - `health/db`: `note: "not using postgres"` (the `error: msg` is a raw DB exception — leave as-is).

6. Keep all changes string-only; preserve trailing punctuation/casing style consistent with the exist

## plan

# Implementation Plan

## Summary

Task 017 finishes the Russian localization of the **Profiles page**. The page (`app/profiles/page.tsx`) is ~90% translated, but a handful of hardcoded English labels remain in the UI, and the supporting API routes plus built-in profile data still emit English. The work is purely string replacement (EN→RU) of **user-visible** text — no logic, schema, or behavior changes. The login route already uses Russian error strings (`"Неверный логин или пароль."`), establishing the convention to follow for the other routes.

## Files To Inspect

Already inspected (findings below):
- `app/profiles/page.tsx` — main page; remaining English labels here.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` shown in the list (English).
- `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts` — `error` JSON strings + `"Untitled"` default name.
- `app/api/analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`, `health/db` routes — `error`/`note` JSON strings.

Worth a quick cross-check (not in scope to edit, but to keep terminology consistent):
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — topic chips render verbatim; decide whether topics are intentionally left in English.
- `components/Toast.tsx` / `components/ConfirmModal.tsx` — confirm toasts already pass Russian; no change needed.

## Implementation Steps

1. **`app/profiles/page.tsx` — remaining visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders raw `fast/balanced/deep` — map to a Russian label (e.g. `Быстрый/Сбалансированный/Глубокий`) via a small lookup, matching the select options below.
   - Line 192: `label="Include keywords"` → `Ключевые слова (включить)`.
   - Line 206: `label="Exclude keywords"` → `Ключевые слова (исключить)`.
   - Lines 234–236: `<option>` labels `Fast`/`Balanced`/`Deep` → Russian (keep `value` attributes `fast`/`balanced`/`deep` unchanged — they are sent to the API).
   - Confirm the placeholder `"добавить…"` (line 299) and all other strings are already Russian (they are).

2. **`src/analysis/profiles.ts` — built-in profile copy:** translate each `description` to Russian. Decide on `name`: these read as product/segment proper nouns (e.g. "AI Security", "IAM Market") — recommend keeping names but translating descriptions, OR translate both for full consistency (see Risks/decision). Do **not** change `id`, `selectedTopics`, or keyword values (those feed matching logic and are domain terms).

3. **`app/api/profiles/route.ts`:** translate the `"Invalid JSON."` error string; translate `"Untitled"` default name → `"Без названия"`.

4. **`app/api/profiles/[id]/route.ts`:** translate `"Profile not found."`, `"Built-in profiles cannot be edited."`, `"Invalid JSON."`, `"Built-in profiles cannot be deleted."`.

5. **Remaining affected API routes** — translate only user-facing `error`/`note` strings to Russian, leaving keys, status codes, and env-var names intact:
   - `analyze`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
   - `benchmark`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
   - `auth/login`: `"Server auth is not configured."`, `"Invalid request."` (note `"Неверный логин или пароль."` is already RU).
   - `auth/logout`: no user-facing strings — no change.
   - `favorites` / `favorites/[id]`: `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
   - `feedback`: `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
   - `health/db`: `note: "not using postgres"` (the `error: msg` is a raw DB exception — leave as-is).

6. Keep all changes string-only; preserve trailing punctuation/casing style consistent with the existing Russian strings.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirm no type breakage from edits

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 017 — Finish Profiles page remaining English labels

## Based On Plan

# Implementation Plan

## Summary

Task 017 finishes the Russian localization of the **Profiles page**. The page (`app/profiles/page.tsx`) is ~90% translated, but a handful of hardcoded English labels remain in the UI, and the supporting API routes plus built-in profile data still emit English. The work is purely string replacement (EN→RU) of **user-visible** text — no logic, schema, or behavior changes. The login route already uses Russian error strings (`"Неверный логин или пароль."`), establishing the convention to follow for the other routes.

## Files To Inspect

Already inspected (findings below):
- `app/profiles/page.tsx` — main page; remaining English labels here.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` shown in the list (English).
- `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts` — `error` JSON strings + `"Untitled"` default name.
- `app/api/analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`, `health/db` routes — `error`/`note` JSON strings.

Worth a quick cross-check (not in scope to edit, but to keep terminology consistent):
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — topic chips render verbatim; decide whether topics are intentionally left in English.
- `components/Toast.tsx` / `components/ConfirmModal.tsx` — confirm toasts already pass Russian; no change needed.

## Implementation Steps

1. **`app/profiles/page.tsx` — remaining visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders raw `fast/balanced/deep` — map to a Russian label (e.g. `Быстрый/Сбалансированный/Глубокий`) via a small lookup, matching the select options below.
   - Line 192: `label="Include keywords"` → `Ключевые слова (включить)`.
   - Line 206: `label="Exclude keywords"` → `Ключевые слова (исключить)`.
   - Lines 234–236: `<option>` labels `Fast`/`Balanced`/`Deep` → Russian (keep `value` attributes `fast`/`balanced`/`deep` unchanged — they are sent to the API).
   - Confirm the placeholder `"добавить…"` (line 299) and all other strings are already Russian (they are).

2. **`src/analysis/profiles.ts` — built-in profile copy:** translate each `description` to Russian. Decide on `name`: these read as product/segment proper nouns (e.g. "AI Security", "IAM Market") — recommend keeping names but translating descriptions, OR translate both for full consistency (see Risks/decision). Do **not** change `id`, `selectedTopics`, or keyword values (those feed matching logic and are domain terms).

3. **`app/api/profiles/route.ts`:** translate the `"Invalid JSON."` error string; translate `"Untitled"` default name → `"Без названия"`.

4. **`app/api/profiles/[id]/route.ts`:** translate `"Profile not found."`, `"Built-in profiles cannot be edited."`, `"Invalid JSON."`, `"Built-in profiles cannot be deleted."`.

5. **Remaining affected API routes** — translate only user-facing `error`/`note` strings to Russian, leaving keys, status codes, and env-var names intact:
   - `analyze`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
   - `benchmark`: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
   - `auth/login`: `"Server auth is not configured."`, `"Invalid request."` (note `"Неверный логин или пароль."` is already RU).
   - `auth/logout`: no user-facing strings — no change.
   - `favorites` / `favorites/[id]`: `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
   - `feedback`: `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
   - `health/db`: `note: "not using postgres"` (the `error: msg` is a raw DB exception — leave as-is).

6. Keep all changes string-only; preserve trailing punctuation/casing style consistent with the existing Russian 
