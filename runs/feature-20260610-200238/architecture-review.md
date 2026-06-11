# Architecture Review

## Feature Request

Add a small Russian helper text under the dashboard page title explaining that this page shows key metrics and trends

## Planner Input

I have everything I need. This is a minimal, single-file change that mirrors a pattern already established on the reports page.

# Implementation Plan

## Summary

Add a small Russian helper text beneath the dashboard page's `<h1>` title, explaining that the page shows key metrics and trends ("ключевые метрики и тренды"). This mirrors the existing helper-text pattern already used on the reports page (`app/reports/page.tsx:59-61`). The change is confined to a single JSX block in `app/dashboard/page.tsx`. None of the other listed "affected files" require edits for this request.

## Files To Inspect

- `app/dashboard/page.tsx` — title block at lines 25–30 (the only file to edit).
- `app/reports/page.tsx` (lines 54–62) — reference for the exact styling/Russian-text convention to match.

## Implementation Steps

1. In `app/dashboard/page.tsx`, locate the title `<div>` (lines 25–30) containing the `eyebrow` span and the `<h1>`.
2. Immediately after the closing `</h1>` (line 29), add a helper paragraph using the established style class:
   ```tsx
   <p className="mt-2 text-sm text-slate-500">
     Здесь показаны ключевые метрики и тренды.
   </p>
   ```
   - Use `text-sm text-slate-500` to match the reports-page primary helper line, or `text-xs text-slate-400` for a smaller subdued line — pick one for consistency with the desired prominence. `text-sm text-slate-500` is recommended as the "small helper under the title."
3. Keep it inside the existing title `<div>` so spacing stays grouped with the heading.

## Validation Steps

1. `npm run build` (or `next build`) / `npx tsc --noEmit` — confirm no type or compile errors.
2. Run the dev server and open `/dashboard`; verify the Russian helper text renders directly under the title, with correct spacing and no layout shift.
3. Confirm Cyrillic text displays correctly (encoding) and wording is grammatically correct.

## Risks

- **Very low risk** — purely additive, presentational JSX with no logic, data, or API changes.
- Minor: ensure the chosen Tailwind classes already exist in the project's utility set (they do — both `text-sm`/`text-slate-500` and `text-xs`/`text-slate-400` are used on the reports page).
- Cosmetic: pick spacing/size consistent with sibling pages to avoid visual inconsistency.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Other: app/dashboard/page.tsx
- API route: app/api/overview/route.ts
- UI component: components/Dashboard.tsx
- Library/module: lib/dashboard.ts
- UI component: components/StatsPanel.tsx
- Other: app/benchmark/page.tsx
- Other: app/collections/page.tsx
- Other: app/feedback/page.tsx
- Other: app/history/page.tsx
- Other: app/login/page.tsx
- Other: app/page.tsx
- Other: app/profiles/page.tsx

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
