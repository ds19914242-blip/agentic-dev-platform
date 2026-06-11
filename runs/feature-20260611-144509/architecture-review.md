# Architecture Review

## Feature Request

Epic task: Task 003 — Translate Hero component

## Planner Input

# Implementation Plan

## Summary

Translate all visible UI text in `components/Hero.tsx` from English to Russian, matching the localization pattern already established in `components/NavBar.tsx` (where all user-facing labels are Russian). The Hero component is a static presentational component with three text elements: an eyebrow tag, a two-line headline (with a gradient-styled phrase), and a descriptive paragraph. No logic, props, or structure changes — only the literal string content. The API route files listed in "Affected Files" contain no user-facing UI copy relevant to this task and should be left untouched.

## Files To Inspect

- `components/Hero.tsx` — the sole file to edit; contains the three English strings.
- `components/NavBar.tsx` — already inspected; reference for tone/register of existing Russian translations (formal "Вы" register, sentence case).
- `app/page.tsx` — confirm where/how `Hero` is rendered, to ensure no surrounding context needs matching changes (e.g. duplicated copy).

## Implementation Steps

1. In `components/Hero.tsx`, translate the three text segments to Russian, preserving JSX structure (`<br />` line break, `gradient-text` span, all className attributes):
   - Eyebrow: `Intelligence Platform` → e.g. `Аналитическая платформа`
   - Headline line 1: `Turn raw feeds into` → e.g. `Превращайте сырые ленты в`
   - Headline gradient phrase: `market intelligence` → e.g. `рыночную аналитику`
   - Paragraph: `Upload a news export, pick your themes, and get a cited TOP-N briefing with trends, signals, and analysis — in minutes.` → e.g. `Загрузите выгрузку новостей, выберите темы и получите краткий обзор ТОП-N со ссылками, трендами, сигналами и анализом — за считанные минуты.`
2. Keep the headline split natural across the `<br />` so the gradient phrase still reads as a continuous clause in Russian (adjust where the line breaks if the Russian word order requires it).
3. Do not alter the API route files — they are listed in the epic's affected-files set but hold no Hero-related UI copy.

## Validation Steps

- Run the type checker / build (`npm run build` or `npx tsc --noEmit`) to confirm no JSX/syntax regressions.
- Run the dev server and load the home page (`app/page.tsx`) to visually confirm the Hero renders the Russian copy, the gradient styling still applies to the highlighted phrase, and the line break/layout looks correct on both mobile and desktop widths.
- Verify the em-dash and "ТОП-N" render correctly (no encoding issues).

## Risks

- **Translation register consistency**: Russian phrasing should match the formal tone used in `NavBar.tsx` and prior translated pages; awkward literal translation of marketing copy ("market intelligence", "cited TOP-N briefing") could read poorly. Minor and easily adjusted.
- **Layout shift**: Russian text is typically longer than English; the headline `max-w-2xl` / paragraph `max-w-md` constraints may wrap differently and change vertical rhythm. Verify visually.
- **Scope creep**: The epic lists many API route files that are unrelated to visible UI text. Editing them risks unintended behavior changes; the plan deliberately limits edits to `Hero.tsx`.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- UI component: components/Hero.tsx
- UI component: components/SourcePicker.tsx
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

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
