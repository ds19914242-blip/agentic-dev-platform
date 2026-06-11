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

6. Keep all changes string-only; preserve trailing punctuation/casing style consistent with the existing Russian strings.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirm no type breakage from edits (option `value`s and API payload keys unchanged).
- `npm run build` / `next build` to ensure the client page compiles.
- Manual smoke (if running the app): open `/profiles` — verify badge, keyword labels, mode dropdown, and card mode text render in Russian; create/edit/delete a profile and confirm toasts + any API error paths show Russian.
- `grep` the edited files for residual ASCII English words in `error:`/`label=`/`<option>`/JSX text to confirm nothing was missed.

## Risks

- **Mode `value` attributes & API payload keys:** translating the visible `<option>` text while accidentally changing its `value` (or the `defaultMode` stored value) would break analysis mode selection. Keep `value="fast|balanced|deep"` and all JSON keys untouched.
- **Built-in profile names — decision needed:** names like "AI Security"/"IAM Market" are domain proper nouns; translating them may reduce recognizability, but leaving them looks half-finished. Recommend translating descriptions and keeping the short English names unless the user wants full translation. (This is the one genuine judgment call — flag for confirmation.)
- **Topic chips (`ALL_TOPICS`) and keyword values** remain English by design (they drive matching). They're visible on the page but out of this task's scope — confirm that's intended so the page doesn't look partially translated.
- **DB exception passthrough** (`health/db` `error: msg`) is raw English from the driver and not safely translatable — intentionally left as-is.
- Scope creep: the affected-files list pulls in many routes only tangentially related to "Profiles." Translating their error strings is low-risk and consistent with the localization epic, but if the intent is strictly the Profiles page, steps 5 can be trimmed to just the two profiles routes.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/profiles/[id]/route.ts
- API route: app/api/profiles/route.ts
- Other: app/profiles/page.tsx
- Other: src/analysis/profiles.ts
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
