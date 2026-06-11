# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 001 — Translate NavBar navigation links

## Planner Input

# Implementation Plan

## Summary

Translate the NavBar navigation links to Russian. On inspection, `components/NavBar.tsx` is the only file holding the navigation UI, and its labels (`LINKS`) plus the logout button are **already in Russian** (matching the established Russian-translation pattern from recent commits). The task therefore reduces to verifying completeness and translating the one remaining untranslated user-facing string: the brand label `"RSS Agent Lab"` (and confirming whether it should stay as a proper noun).

The listed "Affected Files" (API routes under `app/api/**`) contain no navigation UI and are **not relevant** to this task — they are server handlers with no rendered nav links.

## Files To Inspect

- `components/NavBar.tsx` — the only component rendering nav links; already mostly translated.
- `components/Footer.tsx` — confirm no duplicated nav links live here (footer was recently touched in commit `868d0f2`).
- `app/layout.tsx` — confirm `<NavBar />` is the single nav mount point and no other inline nav strings exist.

## Implementation Steps

1. In `components/NavBar.tsx`, confirm every `LINKS[].label` is Russian:
   - `Панель`, `Источники`, `Коллекции`, `Запуск анализа`, `Отчёты`, `Шаблоны`, `Обратная связь`, `Список чтения`, `Настройки` — all already translated.
   - Logout button `Выйти` — already translated.
2. Decide on the brand string `"RSS Agent Lab"` (line 39): typically a product proper noun left as-is. If the task scope includes it, no change; if a Russian label is desired, this is the only edit needed. **Leave as-is unless instructed otherwise** (proper nouns are conventionally untranslated).
3. Make no changes to `href` values, `EXACT` set, routing, or className logic — translation is label-text only.
4. Do **not** modify any `app/api/**` route files; they are out of scope for navigation text.

## Validation Steps

- `npm run build` (or `next build`) / `tsc --noEmit` to confirm no type or syntax regressions.
- Run the app and visually confirm the nav bar renders all nine links plus logout in Russian, with active-link highlighting and routing unchanged.
- Confirm `/login` still hides the nav (early `return null`).

## Risks

- **Likely no-op:** the translation appears already complete (probably done in commit `9fcb163`). Re-verify before opening a PR to avoid an empty changeset.
- **Scope creep:** the supplied "Affected Files" point at API routes that have nothing to do with nav links — editing them would be incorrect.
- **Brand-name ambiguity:** translating `"RSS Agent Lab"` is a judgment call; defaulting to leaving proper nouns untranslated avoids an unwanted change.


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


## plan

# Implementation Plan

## Summary

Translate the NavBar navigation links to Russian. On inspection, `components/NavBar.tsx` is the only file holding the navigation UI, and its labels (`LINKS`) plus the logout button are **already in Russian** (matching the established Russian-translation pattern from recent commits). The task therefore reduces to verifying completeness and translating the one remaining untranslated user-facing string: the brand label `"RSS Agent Lab"` (and confirming whether it should stay as a proper noun).

The listed "Affected Files" (API routes under `app/api/**`) contain no navigation UI and are **not relevant** to this task — they are server handlers with no rendered nav links.

## Files To Inspect

- `components/NavBar.tsx` — the only component rendering nav links; already mostly translated.
- `components/Footer.tsx` — confirm no duplicated nav links live here (footer was recently touched in commit `868d0f2`).
- `app/layout.tsx` — confirm `<NavBar />` is the single nav mount point and no other inline nav strings exist.

## Implementation Steps

1. In `components/NavBar.tsx`, confirm every `LINKS[].label` is Russian:
   - `Панель`, `Источники`, `Коллекции`, `Запуск анализа`, `Отчёты`, `Шаблоны`, `Обратная связь`, `Список чтения`, `Настройки` — all already translated.
   - Logout button `Выйти` — already translated.
2. Decide on the brand string `"RSS Agent Lab"` (line 39): typically a product proper noun left as-is. If the task scope includes it, no change; if a Russian label is desired, this is the only edit needed. **Leave as-is unless instructed otherwise** (proper nouns are conventionally untranslated).
3. Make no changes to `href` values, `EXACT` set, routing, or className logic — translation is label-text only.
4. Do **not** modify any `app/api/**` route files; they are out of scope for navigation text.

## Validation Steps

- `npm run build` (or `next build`) / `tsc --noEmit` to confirm no type or syntax regressions.
- Run the app and visually confirm the nav bar renders all nine links plus logout in Russian, with active-link highlighting and routing unchanged.
- Confirm `/login` still hides the nav (early `return null`).

## Risks

- **Likely no-op:** the translation appears already complete (probably done in commit `9fcb163`). Re-verify before opening a PR to avoid an empty changeset.
- **Scope creep:** the supplied "Affected Files" point at API routes that have nothing to do with nav links — editing them would be incorrect.
- **Brand-name ambiguity:** translating `"RSS Agent Lab"` is a judgment call; defaulting to leaving proper nouns untranslated avoids an unwanted change.


## qa_plan

# QA Plan

## Feature Request

Epic task: Task 001 — Translate NavBar navigation links

## Based On Plan

# Implementation Plan

## Summary

Translate the NavBar navigation links to Russian. On inspection, `components/NavBar.tsx` is the only file holding the navigation UI, and its labels (`LINKS`) plus the logout button are **already in Russian** (matching the established Russian-translation pattern from recent commits). The task therefore reduces to verifying completeness and translating the one remaining untranslated user-facing string: the brand label `"RSS Agent Lab"` (and confirming whether it should stay as a proper noun).

The listed "Affected Files" (API routes under `app/api/**`) contain no navigation UI and are **not relevant** to this task — they are server handlers with no rendered nav links.

## Files To Inspect

- `components/NavBar.tsx` — the only component rendering nav links; already mostly translated.
- `components/Footer.tsx` — confirm no duplicated nav links live here (footer was recently touched in commit `868d0f2`).
- `app/layout.tsx` — confirm `<NavBar />` is the single nav mount point and no other inline nav strings exist.

## Implementation Steps

1. In `components/NavBar.tsx`, confirm every `LINKS[].label` is Russian:
   - `Панель`, `Источники`, `Коллекции`, `Запуск анализа`, `Отчёты`, `Шаблоны`, `Обратная связь`, `Список чтения`, `Настройки` — all already translated.
   - Logout button `Выйти` — already translated.
2. Decide on the brand string `"RSS Agent Lab"` (line 39): typically a product proper noun left as-is. If the task scope includes it, no change; if a Russian label is desired, this is the only edit needed. **Leave as-is unless instructed otherwise** (proper nouns are conventionally untranslated).
3. Make no changes to `href` values, `EXACT` set, routing, or className logic — translation is label-text only.
4. Do **not** modify any `app/api/**` route files; they are out of scope for navigation text.

## Validation Steps

- `npm run build` (or `next build`) / `tsc --noEmit` to confirm no type or syntax regressions.
- Run the app and visually confirm the nav bar renders all nine links plus logout in Russian, with active-link highlighting and routing unchanged.
- Confirm `/login` still hides the nav (early `return null`).

## Risks

- **Likely no-op:** the translation appears already complete (probably done in commit `9fcb163`). Re-verify before opening a PR to avoid an empty changeset.
- **Scope creep:** the supplied "Affected Files" point at API routes that have nothing to do with nav links — editing them would be incorrect.
- **Brand-name ambiguity:** translating `"RSS Agent Lab"` is a judgment call; defaulting to leaving proper nouns untranslated avoids an unwanted change.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 001 — Translate NavBar navigation links

## Planner Input

# Implementation Plan

## Summary

Translate the NavBar navigation links to Russian. On inspection, `components/NavBar.tsx` is the only file holding the navigation UI, and its labels (`LINKS`) plus the logout button are **already in Russian** (matching the established Russian-translation pattern from recent commits). The task therefore reduces to verifying completeness and translating the one remaining untranslated user-facing string: the brand label `"RSS Agent Lab"` (and confirming whether it should stay as a proper noun).

The listed "Affected Files" (API routes under `app/api/**`) contain no navigation UI and are **not relevant** to this task — they are server handlers with no rendered nav links.

## Files To Inspect

- `components/NavBar.tsx` — the only component rendering nav links; already mostly translated.
- `components/Footer.tsx` — confirm no duplicated nav links live here (footer was recently touched in commit `868d0f2`).
- `app/layout.tsx` — confirm `<NavBar />` is the single nav mount point and no other inline nav strings exist.

## Implementation Steps

1.
