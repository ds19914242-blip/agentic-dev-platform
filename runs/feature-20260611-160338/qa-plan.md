# QA Plan

## Feature Request

Epic task: Task 015 — Finish home page (page.tsx) remaining English

## Based On Plan

I have what I need. The task is clearly about translating the remaining English UI strings in `app/page.tsx` to Russian (consistent with prior commits in this repo). The listed API routes are not relevant to the visible home-page text and should not be touched.

# Implementation Plan

## Summary

`app/page.tsx` is mostly already in Russian, but a handful of user-facing English strings remain in the "empty/uploading" (RSS collection) branch, the preview action button, and two error messages. This task finishes the localization of the home page by translating those remaining strings to Russian, matching the tone/style already used elsewhere in the file (e.g. "← Другой файл", "Выберите хотя бы одну тему"). No logic, props, state, or API behavior changes — text only.

## Files To Inspect

- `app/page.tsx` — the only file to change (already read; all remaining English located).
- `components/Hero.tsx`, `components/SourcePicker.tsx` (quick glance only) — to confirm the "RSS collection" label and source-type wording match terminology used in child components, so the page stays consistent. Not to be edited under this task.

## Implementation Steps

Translate the following user-visible English strings in `app/page.tsx` (leave code identifiers, `PerformanceMode`, console/internal values untouched):

1. **Line 162** — `setError("Job not found. Please start analysis again.")` → e.g. `"Задание не найдено. Запустите анализ заново."`
2. **Line 169** — same string in the `not_found` branch → same translation as above.
3. **Line 212** — `<p className="label mb-2">RSS collection</p>` → `"RSS-коллекция"` (or "Коллекция RSS", matching SourcePicker wording).
4. **Lines 214–219** — "No collections yet — create one and add sources first." Translate the surrounding text while keeping the `<a href="/rss/collections">…</a>` link element; e.g. `"Пока нет коллекций — "` + link text `"создайте коллекцию"` + `" и сначала добавьте источники."`
5. **Line 228** — `<option value="">Choose a collection…</option>` → `"Выберите коллекцию…"`
6. **Line 232** — `({c.sourceIds.length} sources)` → `({c.sourceIds.length} источн.)` (use a count-appropriate Russian word; keep it short for the dropdown).
7. **Line 240** — `collecting ? "Collecting articles…" : "Collect Articles →"` → e.g. `"Сбор статей…"` / `"Собрать статьи →"`.
8. **Line 286** — `Run Analysis →` → `"Запустить анализ →"`.

Preserve all JSX structure, whitespace literals (`{" "}`), arrows (→, ←), and ellipsis characters.

## Validation Steps

- Run the type/build check (`npm run build` or `npx tsc --noEmit`) to confirm no JSX/TS breakage from the edits.
- Visually scan `app/page.tsx` to confirm no English user-facing strings remain (search for ASCII-letter strings inside JSX text and button/option labels).
- If feasible, start the dev server and load `/` to confirm the empty state, RSS branch, preview action bar, and an error state render the Russian text correctly.

## Risks

- **Scope creep**: the affected-files list points at API routes; these contain server-side error strings unrelated to the home page UI. Editing them is out of scope for "home page (page.tsx)" and risks changing API error contracts — leave them alone unless the task is later clarified.
- **Consistency**: terminology ("коллекция", "источники", "анализ") should match existing translations in NavBar/other pages to avoid mixed wording; quick cross-check recommended.
- **Pluralization**: Russian noun forms depend on count (источник/источника/источников). A single short fixed form ("источн.") avoids incorrect grammar without adding pluralization logic.
- Very low overall risk — text-only changes in one client component.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 015 — Finish home page (page.tsx) remaining English

## Planner Input

I have what I need. The task is clearly about translating the remaining English UI strings in `app/page.tsx` to Russian (consistent with prior commits in this repo). The listed API routes are not relevant to the visible home-page text and should not be touched.

# Implementation Plan

## Summary

`app/page.tsx` is mostly already in Russian, but a handful of user-facing English strings remain in the "empty/uploading" (RSS collection) branch, the preview action button, and two error messages. This task finishes the localization of the home page by translating those remaining strings to Russian, matching the tone/style already used elsewhere in the file (e.g. "← Другой файл", "Выберите хотя бы одну тему"). No logic, props, state, or API behavior changes — text only.

## Files To Inspect

- `app/page.tsx` — the only file to change (already read; all remaining English located).
- `components/Hero.tsx`, `components/SourcePicker.tsx` (quick glance only) — to confirm the "RSS collection" label and source-type wording match terminology used in child components, so the page stays consistent. Not to be edited under this task.

## Implementation Steps

Translate the following user-visible English strings in `app/page.tsx` (leave code identifiers, `PerformanceMode`, console/internal values untouched):

1. **Line 162** — `setError("Job not found. Please start analysis again.")` → e.g. `"Задание не найдено. Запустите анализ заново."`
2. **Line 169** — same string in the `not_found` branch → same translation as above.
3. **Line 212** — `<p className="label mb-2">RSS collection</p>` → `"RSS-коллекция"` (or "Коллекция RSS", matching SourcePicker wording).
4. **Lines 214–219** — "No collections yet — create one and add sources first." Translate the surrounding text while keeping the `<a href="/rss/collections">…</a>` link element; e.g. `"Пока нет коллекций — "` + link text `"создайте коллекцию"` + `" и сначала добавьте источники."`
5. **Line 228** — `<option value="">Choose a collection…</option>` → `"Выберите коллекцию…"`
6. **Line 232** — `({c.sourceIds.length} sources)` → `({c.sourceIds.length} источн.)` (use a count-appropriate Russian word; keep it short for the dropdown).
7. **Line 240** — `collecting ? "Collecting articles…" : "Collect Articles →"` → e.g. `"Сбор статей…"` / `"Собрать статьи →"`.
8. **Line 286** — `Run Analysis →` → `"Запустить анализ →"`.

Preserve all JSX structure, whitespace literals (`{" "}`), arrows (→, ←), and ellipsis characters.

## Validation Steps

- Run the type/build check (`npm run build` or `npx tsc --noEmit`) to confirm no JSX/TS breakage from the edits.
- Visually scan `app/page.tsx` to confirm no English user-facing strings remain (search for ASCII-letter strings inside JSX text and button/option labels).
- If feasible, start the dev server and load `/` to confirm the empty state, RSS branch, preview action bar, and an error state render the Russian text correctly.

## Risks

- **Scope creep**: the affected-files list points at API routes; these contain server-side error strings unrelated to the home page UI. Editing them is out of scope for "home page (page.tsx)" and risks changing API error contracts — leave them alone unless the task is later clarified.
- **Consistency**: terminology ("коллекция", "источники", "анализ") should match existing translations in NavBar/other pages to avoid mixed wording; quick cross-check recommended.
- **Pluralization**: Russian noun forms depend on count (источник/источника/источников). A single short fixed form ("источн.") avoids incorrect grammar without adding pluralization logic.
- Very low overall risk — text-only changes in one client component.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts
- API route: app/api/health/route.ts
- API route: app/api/jobs/[jobId]/route.ts
- API route: app/api/overview/route.ts
- API route: app/api/profiles/[id]/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- app/api/analyze/route.ts
- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/api/benchmark/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts
- app/api/feedback/route.ts
- app/api/health/db/route.ts
- app/api/health/route.ts
- app/api/jobs/[jobId]/route.ts
- app/api/overview/route.ts
- app/api/profiles/[id]/route.ts

## Required Command

```bash
npx tsc --noEmit
```