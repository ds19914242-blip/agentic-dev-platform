# Architecture Review

## Feature Request

Add a small Russian helper text under the reports page title explaining that generated reports can be reviewed and exported here

## Planner Input

# Implementation Plan

## Summary

Add a small Russian helper text beneath the reports page title (`app/reports/page.tsx`) telling the user that generated reports can be reviewed and exported on this page. This is a single-file, presentation-only change — no API, export, or data-layer code is involved despite the breadth of the "Affected Files" list.

## Files To Inspect

- `app/reports/page.tsx` — already inspected. The page header lives at lines 54–59:
  - line 55: `<h1>Reports</h1>` (currently English)
  - lines 56–58: an existing subtitle `<p class="mt-1 text-sm text-slate-500">Saved analyses — open without re-running Claude.</p>`

  Note the existing date already uses `"ru-RU"` locale (line 111), confirming Russian is an accepted language for this page.

The remaining listed files (`app/api/report/**`, `lib/export/**`, `src/report*.ts`, `src/reporting/**`, importers) describe the report-generation/export pipeline. They are useful context for *why* the text is accurate, but require **no edits** for this request.

## Implementation Steps

1. In `app/reports/page.tsx`, within the existing header `<div>` (lines 54–59), add a new helper-text paragraph under the `<h1>` title. Reuse the existing subtitle styling for consistency: `className="mt-1 text-sm text-slate-500"`.
2. Suggested Russian copy (single short sentence):
   > «Здесь можно просмотреть сгенерированные отчёты и экспортировать их.»
3. Decide placement relative to the existing English subtitle (line 56–58):
   - **Recommended:** place the Russian helper text directly under `<h1>`, and either keep or remove the existing English subtitle depending on whether a mixed-language header is acceptable. Cleanest result: add the Russian text as its own `<p>` immediately after the title.
4. Keep the change confined to JSX inside the header block; no new imports, state, or props are needed.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck script) — confirm no TS errors.
- `npm run lint` if configured.
- Run the dev server and open `/reports`; confirm the Russian helper text renders under the title with correct styling and no layout shift.
- Verify Cyrillic characters display correctly (encoding/font).

## Risks

- **Very low.** Static text addition to one client component.
- Minor UX/consistency consideration: the page currently mixes English (title/subtitle) and Russian (date locale). Adding Russian helper text continues this mix; confirm whether the title/subtitle should also be Russian for consistency, or leave scope limited to just the requested helper text.
- Ensure the file is saved as UTF-8 so Cyrillic text is not corrupted.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/report/[id]/docx/route.ts
- API route: app/api/report/[id]/json/route.ts
- API route: app/api/report/[id]/markdown/route.ts
- API route: app/api/report/[id]/pdf/route.ts
- Other: src/reportJson.ts
- Other: app/reports/page.tsx
- Library/module: lib/export/docx.ts
- Library/module: lib/export/pdf.ts
- Other: src/importers/loadArticlesJson.ts
- Other: src/report.ts
- Other: src/reporting/renderCustomerReport.ts
- Other: src/reporting/transparency.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
