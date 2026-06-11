# QA Plan

## Feature Request

Epic task: Task 015 — Finish home page (page.tsx) remaining English

## Based On Plan

# Implementation Plan

## Summary

Task 015 finishes the Russian localization of the home page (`app/page.tsx`). Earlier commits in this epic already translated most error messages and several buttons, but a handful of user-visible English strings remain — primarily in the RSS-collection source block and a couple of action buttons / error toasts. The change is UI-text-only: replace the remaining English strings with Russian, matching the tone and style already established in the file (e.g. `"Не удалось собрать статьи."`, `"← Другой файл"`).

Note: the "Affected Files" list enumerates `app/api/**` route handlers, but the epic title and actual remaining English are in `app/page.tsx`. API route files return machine-readable JSON / error codes consumed by the UI — they are **not** visible UI text and should not be touched. Scope is strictly the home page's rendered strings.

## Files To Inspect

- `app/page.tsx` — the only file to edit; remaining English strings identified below.
- `components/Hero.tsx`, `components/SourcePicker.tsx`, `components/UploadDropzone.tsx`, `components/ProgressTimeline.tsx`, `components/ErrorState.tsx`, `components/Dashboard.tsx` — confirm these child components are already localized (out of scope for this task, but verify the home page reads consistently).
- Recent epic commits (`git log`) — confirm Russian phrasing/tone conventions already adopted.

## Implementation Steps

Translate the remaining English user-visible strings in `app/page.tsx` to Russian:

1. **Job-not-found error messages** (lines ~162 and ~169): `"Job not found. Please start analysis again."` → e.g. `"Задание не найдено. Запустите анализ заново."` (both occurrences).
2. **RSS collection label** (line ~212): `"RSS collection"` → e.g. `"RSS-коллекция"`.
3. **Empty-collections notice** (lines ~214–219): `"No collections yet —"`, link text `"create one"`, and `"and add sources first."` → Russian equivalents (e.g. `"Коллекций пока нет — "`, `"создайте одну"`, `" и сначала добавьте источники."`).
4. **Select placeholder** (line ~228): `"Choose a collection…"` → e.g. `"Выберите коллекцию…"`.
5. **Source count suffix** (line ~232): `({c.sourceIds.length} sources)` → e.g. `({c.sourceIds.length} источников)`.
6. **Collect button** (line ~240): `"Collecting articles…"` → e.g. `"Сбор статей…"`; `"Collect Articles →"` → e.g. `"Собрать статьи →"`.
7. **Run Analysis button** (line ~286): `"Run Analysis →"` → e.g. `"Запустить анализ →"`.

Constraints:
- Change only string literals rendered to the user. Do **not** alter `Phase` type values, state keys, `sessionStorage` keys, API paths, CSS classes, or JSON request fields.
- Leave the code comment on line ~184 (`/* transient — keep polling */`) and other non-visible comments as-is (optional to translate; not user-facing).
- Keep arrow glyphs (`→`, `←`) and ellipses intact.

## Validation Steps

- `npm run lint` / `npx tsc --noEmit` (or the repo's typecheck script) — ensure no syntax/type regressions from the string edits.
- `npm run build` (Next.js) to confirm the page compiles.
- Manually run the app and walk the home page through each phase: empty (TXT + RSS source pickers), the empty-collections notice, collection select + collect button states, preview → run analysis, and the job-not-found error path — verifying every previously-English string now renders in Russian and no English remains.
- Grep `app/page.tsx` for residual Latin-letter UI strings to confirm completeness.

## Risks

- **Scope creep**: the affected-files list points at API routes; editing them would change machine-readable error codes/contract. Confirmed out of scope — UI-only change.
- **Hidden English in child components**: strings like the Hero, dropzone, and dashboard come from child components; if any still show English they belong to other epic tasks, not this one — note but don't expand scope.
- **Encoding**: ensure the file stays UTF-8 so Cyrillic renders correctly.
- **Tone consistency**: match the imperative/polite style already used in existing Russian strings in the same file.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 015 — Finish home page (page.tsx) remaining English

## Planner Input

# Implementation Plan

## Summary

Task 015 finishes the Russian localization of the home page (`app/page.tsx`). Earlier commits in this epic already translated most error messages and several buttons, but a handful of user-visible English strings remain — primarily in the RSS-collection source block and a couple of action buttons / error toasts. The change is UI-text-only: replace the remaining English strings with Russian, matching the tone and style already established in the file (e.g. `"Не удалось собрать статьи."`, `"← Другой файл"`).

Note: the "Affected Files" list enumerates `app/api/**` route handlers, but the epic title and actual remaining English are in `app/page.tsx`. API route files return machine-readable JSON / error codes consumed by the UI — they are **not** visible UI text and should not be touched. Scope is strictly the home page's rendered strings.

## Files To Inspect

- `app/page.tsx` — the only file to edit; remaining English strings identified below.
- `components/Hero.tsx`, `components/SourcePicker.tsx`, `components/UploadDropzone.tsx`, `components/ProgressTimeline.tsx`, `components/ErrorState.tsx`, `components/Dashboard.tsx` — confirm these child components are already localized (out of scope for this task, but verify the home page reads consistently).
- Recent epic commits (`git log`) — confirm Russian phrasing/tone conventions already adopted.

## Implementation Steps

Translate the remaining English user-visible strings in `app/page.tsx` to Russian:

1. **Job-not-found error messages** (lines ~162 and ~169): `"Job not found. Please start analysis again."` → e.g. `"Задание не найдено. Запустите анализ заново."` (both occurrences).
2. **RSS collection label** (line ~212): `"RSS collection"` → e.g. `"RSS-коллекция"`.
3. **Empty-collections notice** (lines ~214–219): `"No collections yet —"`, link text `"create one"`, and `"and add sources first."` → Russian equivalents (e.g. `"Коллекций пока нет — "`, `"создайте одну"`, `" и сначала добавьте источники."`).
4. **Select placeholder** (line ~228): `"Choose a collection…"` → e.g. `"Выберите коллекцию…"`.
5. **Source count suffix** (line ~232): `({c.sourceIds.length} sources)` → e.g. `({c.sourceIds.length} источников)`.
6. **Collect button** (line ~240): `"Collecting articles…"` → e.g. `"Сбор статей…"`; `"Collect Articles →"` → e.g. `"Собрать статьи →"`.
7. **Run Analysis button** (line ~286): `"Run Analysis →"` → e.g. `"Запустить анализ →"`.

Constraints:
- Change only string literals rendered to the user. Do **not** alter `Phase` type values, state keys, `sessionStorage` keys, API paths, CSS classes, or JSON request fields.
- Leave the code comment on line ~184 (`/* transient — keep polling */`) and other non-visible comments as-is (optional to translate; not user-facing).
- Keep arrow glyphs (`→`, `←`) and ellipses intact.

## Validation Steps

- `npm run lint` / `npx tsc --noEmit` (or the repo's typecheck script) — ensure no syntax/type regressions from the string edits.
- `npm run build` (Next.js) to confirm the page compiles.
- Manually run the app and walk the home page through each phase: empty (TXT + RSS source pickers), the empty-collections notice, collection select + collect button states, preview → run analysis, and the job-not-found error path — verifying every previously-English string now renders in Russian and no English remains.
- Grep `app/page.tsx` for residual Latin-letter UI strings to confirm completeness.

## Risks

- **Scope creep**: the affected-files list points at API routes; editing them would change machine-readable error codes/contract. Confirmed out of scope — UI-only change.
- **Hidden English in child components**: strings like the Hero, dropzone, and dashboard come from child components; if any still show English they belong to other epic tasks, not this one — note but don't expand scope.
- **Encoding**: ensure the file stays UTF-8 so Cyrillic renders correctly.
- **Tone consistency**: match the imperative/polite style already used in existing Russian strings in the same file.


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