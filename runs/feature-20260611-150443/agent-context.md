# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 008 — Translate Feedback page

## Planner Input

I have enough context. The established pattern (from prior "Translate" commits) is translating user-facing English UI strings to Russian in the page's `.tsx` file only — the API routes and analysis files in the affected list are not touched.

# Implementation Plan

## Summary

Translate all user-facing English strings on the Feedback page (`app/feedback/page.tsx`) to Russian, matching the established pattern from prior translation tasks (e.g. Task 006, which edited only the page's `.tsx` and left strings like the `ru-RU` date locale and class names intact). No API routes, analysis files, or logic are modified — only display text. The page already has one Russian helper line; this completes the localization.

## Files To Inspect

- `app/feedback/page.tsx` — the only file requiring edits (already read; all target strings identified).
- Reference only (no changes): `app/settings/page.tsx` and prior commits `4764b69`/`51eb9ef` for translation tone/terminology consistency (e.g. "Релевантно", "Не релевантно", "Пропущено, но релевантно").

## Implementation Steps

1. **`VOTE_LABEL` record** (lines 7–11): translate values to Russian — `relevant → "Релевантно"`, `not_relevant → "Не релевантно"`, `missed_but_relevant → "Пропущено, но релевантно"` (reuse terminology already established in the Settings translation for consistency).
2. **Header** (line 40): `"Feedback Center"` → `"Центр отзывов"`.
3. **Header description** (lines 41–43): translate, keeping the Settings reference, e.g. `"Ваши оценки релевантности влияют на будущее ранжирование (см. Настройки → Влияние отзывов)."` — note "Settings → Feedback Influence" should match the already-translated Settings page labels ("Настройки" / "Влияние отзывов").
4. **Redundant Russian sub-line** (lines 44–46): leave as-is or fold into the description; recommend keeping it since it's already Russian and consistent.
5. **`KpiCard` labels** (lines 50–56): `"Relevant"` → `"Релевантно"`, `"Not Relevant"` → `"Не релевантно"`, `"Missed But Relevant"` → `"Пропущено, но релевантно"`.
6. **Filter "All" button** (line 66): `"All"` → `"Все"` (the other filter buttons already render via the translated `VOTE_LABEL`).
7. **Empty states** (lines 74–76): `"No feedback yet — vote on articles in a report."` → `"Пока нет отзывов — оцените статьи в отчёте."`; `"Nothing for this filter."` → `"Нет данных для этого фильтра."`.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirm no type errors; translations are string-value-only so types are unaffected.
- `npm run lint` if configured.
- Visual: run the app, open `/feedback`, verify header, KPI cards, filter chips (including "Все"), and both empty-state messages render in Russian; confirm filtering still works (logic untouched).
- Confirm `git diff` touches only `app/feedback/page.tsx` and contains no logic/key changes (the `FeedbackVote` keys `relevant`/`not_relevant`/`missed_but_relevant` must remain unchanged — only their display labels change).

## Risks

- **Low overall.** Only display strings change.
- **Key vs. label confusion**: the union keys (`relevant`, etc.) are also used as data values and `Record` keys — must not be translated, only the mapped label values. Translating a key would break vote matching and styling.
- **Terminology drift**: ensure Russian terms match the already-translated Settings page so the cross-reference in the header description stays coherent.
- **Scope creep**: the affected-files list includes many API routes that contain no user-facing UI strings; per the prior task pattern these should not be edited. Touching them risks unintended behavior changes.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/feedback/r

## plan

I have enough context. The established pattern (from prior "Translate" commits) is translating user-facing English UI strings to Russian in the page's `.tsx` file only — the API routes and analysis files in the affected list are not touched.

# Implementation Plan

## Summary

Translate all user-facing English strings on the Feedback page (`app/feedback/page.tsx`) to Russian, matching the established pattern from prior translation tasks (e.g. Task 006, which edited only the page's `.tsx` and left strings like the `ru-RU` date locale and class names intact). No API routes, analysis files, or logic are modified — only display text. The page already has one Russian helper line; this completes the localization.

## Files To Inspect

- `app/feedback/page.tsx` — the only file requiring edits (already read; all target strings identified).
- Reference only (no changes): `app/settings/page.tsx` and prior commits `4764b69`/`51eb9ef` for translation tone/terminology consistency (e.g. "Релевантно", "Не релевантно", "Пропущено, но релевантно").

## Implementation Steps

1. **`VOTE_LABEL` record** (lines 7–11): translate values to Russian — `relevant → "Релевантно"`, `not_relevant → "Не релевантно"`, `missed_but_relevant → "Пропущено, но релевантно"` (reuse terminology already established in the Settings translation for consistency).
2. **Header** (line 40): `"Feedback Center"` → `"Центр отзывов"`.
3. **Header description** (lines 41–43): translate, keeping the Settings reference, e.g. `"Ваши оценки релевантности влияют на будущее ранжирование (см. Настройки → Влияние отзывов)."` — note "Settings → Feedback Influence" should match the already-translated Settings page labels ("Настройки" / "Влияние отзывов").
4. **Redundant Russian sub-line** (lines 44–46): leave as-is or fold into the description; recommend keeping it since it's already Russian and consistent.
5. **`KpiCard` labels** (lines 50–56): `"Relevant"` → `"Релевантно"`, `"Not Relevant"` → `"Не релевантно"`, `"Missed But Relevant"` → `"Пропущено, но релевантно"`.
6. **Filter "All" button** (line 66): `"All"` → `"Все"` (the other filter buttons already render via the translated `VOTE_LABEL`).
7. **Empty states** (lines 74–76): `"No feedback yet — vote on articles in a report."` → `"Пока нет отзывов — оцените статьи в отчёте."`; `"Nothing for this filter."` → `"Нет данных для этого фильтра."`.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirm no type errors; translations are string-value-only so types are unaffected.
- `npm run lint` if configured.
- Visual: run the app, open `/feedback`, verify header, KPI cards, filter chips (including "Все"), and both empty-state messages render in Russian; confirm filtering still works (logic untouched).
- Confirm `git diff` touches only `app/feedback/page.tsx` and contains no logic/key changes (the `FeedbackVote` keys `relevant`/`not_relevant`/`missed_but_relevant` must remain unchanged — only their display labels change).

## Risks

- **Low overall.** Only display strings change.
- **Key vs. label confusion**: the union keys (`relevant`, etc.) are also used as data values and `Record` keys — must not be translated, only the mapped label values. Translating a key would break vote matching and styling.
- **Terminology drift**: ensure Russian terms match the already-translated Settings page so the cross-reference in the header description stays coherent.
- **Scope creep**: the affected-files list includes many API routes that contain no user-facing UI strings; per the prior task pattern these should not be edited. Touching them risks unintended behavior changes.


## qa_plan

# QA Plan

## Feature Request

Epic task: Task 008 — Translate Feedback page

## Based On Plan

I have enough context. The established pattern (from prior "Translate" commits) is translating user-facing English UI strings to Russian in the page's `.tsx` file only — the API routes and analysis files in the affected list are not touched.

# Implementation Plan

## Summary

Translate all user-facing English strings on the Feedback page (`app/feedback/page.tsx`) to Russian, matching the established pattern from prior translation tasks (e.g. Task 006, which edited only the page's `.tsx` and left strings like the `ru-RU` date locale and class names intact). No API routes, analysis files, or logic are modified — only display text. The page already has one Russian helper line; this completes the localization.

## Files To Inspect

- `app/feedback/page.tsx` — the only file requiring edits (already read; all target strings identified).
- Reference only (no changes): `app/settings/page.tsx` and prior commits `4764b69`/`51eb9ef` for translation tone/terminology consistency (e.g. "Релевантно", "Не релевантно", "Пропущено, но релевантно").

## Implementation Steps

1. **`VOTE_LABEL` record** (lines 7–11): translate values to Russian — `relevant → "Релевантно"`, `not_relevant → "Не релевантно"`, `missed_but_relevant → "Пропущено, но релевантно"` (reuse terminology already established in the Settings translation for consistency).
2. **Header** (line 40): `"Feedback Center"` → `"Центр отзывов"`.
3. **Header description** (lines 41–43): translate, keeping the Settings reference, e.g. `"Ваши оценки релевантности влияют на будущее ранжирование (см. Настройки → Влияние отзывов)."` — note "Settings → Feedback Influence" should match the already-translated Settings page labels ("Настройки" / "Влияние отзывов").
4. **Redundant Russian sub-line** (lines 44–46): leave as-is or fold into the description; recommend keeping it since it's already Russian and consistent.
5. **`KpiCard` labels** (lines 50–56): `"Relevant"` → `"Релевантно"`, `"Not Relevant"` → `"Не релевантно"`, `"Missed But Relevant"` → `"Пропущено, но релевантно"`.
6. **Filter "All" button** (line 66): `"All"` → `"Все"` (the other filter buttons already render via the translated `VOTE_LABEL`).
7. **Empty states** (lines 74–76): `"No feedback yet — vote on articles in a report."` → `"Пока нет отзывов — оцените статьи в отчёте."`; `"Nothing for this filter."` → `"Нет данных для этого фильтра."`.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirm no type errors; translations are string-value-only so types are unaffected.
- `npm run lint` if configured.
- Visual: run the app, open `/feedback`, verify header, KPI cards, filter chips (including "Все"), and both empty-state messages render in Russian; confirm filtering still works (logic untouched).
- Confirm `git diff` touches only `app/feedback/page.tsx` and contains no logic/key changes (the `FeedbackVote` keys `relevant`/`not_relevant`/`missed_but_relevant` must remain unchanged — only their display labels change).

## Risks

- **Low overall.** Only display strings change.
- **Key vs. label confusion**: the union keys (`relevant`, etc.) are also used as data values and `Record` keys — must not be translated, only the mapped label values. Translating a key would break vote matching and styling.
- **Terminology drift**: ensure Russian terms match the already-translated Settings page so the cross-reference in the header description stays coherent.
- **Scope creep**: the affected-files list includes many API routes that contain no user-facing UI strings; per the prior task pattern these should not be edited. Touching them risks unintended behavior changes.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 008 — Translate Feedback page

## Planner Input

I have enough context. The established pattern (from prior "Translate" commits) is translating user-facing English UI stri
