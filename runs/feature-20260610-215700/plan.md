I have everything I need. The reports page established the exact pattern to mirror.

# Implementation Plan

## Summary

Add a small Russian helper sentence beneath the Feedback page title, styled subtly, explaining that submitting feedback improves future article rankings. This mirrors the pattern already established on the reports page (`app/reports/page.tsx:59-61`). It is a single-line, view-only UI change — no API, data, or logic changes required.

## Files To Inspect

- `app/feedback/page.tsx:39-44` — the title block where the new helper text will be inserted (already contains an English `<p>` subtitle about ranking influence).
- `app/reports/page.tsx:54-61` — reference for the exact Russian helper-text styling convention (`mt-1 text-xs text-slate-400`).

## Implementation Steps

1. In `app/feedback/page.tsx`, inside the title `<div>` (lines 39-44), add a new paragraph directly after the existing `<p>` (line 43), before the closing `</div>`:
   ```tsx
   <p className="mt-1 text-xs text-slate-400">
     Ваши отзывы помогают улучшать ранжирование новостей в будущих отчётах.
   </p>
   ```
2. Keep the existing English subtitle as-is (only the request's scope is adding the new Russian helper line; do not alter unrelated text unless consistency with the reports page is desired — out of scope here).

## Validation Steps

- Run the dev server and open `/feedback`; confirm the new Russian line renders under the title in muted small text, with no layout shift.
- `npm run build` (or `tsc`) to confirm no JSX/type errors introduced.

## Risks

- Minimal. Only a static text node is added; no behavior, state, or data flow is touched.
- The other 11 "Affected Files" listed (API routes, importers, ranking logic) are not relevant to this UI-only change and should not be modified — touching them would expand scope and add risk.
- Minor inconsistency: the page title and existing subtitle remain in English while the new line is Russian. Acceptable per the request, but flag to the user if full-page localization is preferred.
