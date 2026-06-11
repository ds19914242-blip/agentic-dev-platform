# Implementation Plan

## Summary

Add a small Russian helper paragraph directly under the "Отчёты" page title that tells the user reports can be reviewed and exported on this page (e.g. *"Здесь можно просматривать и экспортировать отчёты."*). This is a single, self-contained UI text change in the reports page header block.

> ⚠️ **Note:** An equivalent helper line already exists in the current code at `app/reports/page.tsx:59-61`:
> *"Здесь можно просматривать и экспортировать сформированные отчёты."*
> If this satisfies the request, **no change is needed**. The plan below assumes you want to add/adjust this helper text (e.g. reword it, restyle it, or it was reverted). Of the 12 "affected files" listed, only `app/reports/page.tsx` is relevant — the export routes and reporting modules are unrelated to a title helper text and should not be touched.

## Files To Inspect

- `app/reports/page.tsx` — the only file to change; header block is at lines 53–62. Existing helper text candidate at lines 59–61.
- `app/globals.css` — only if a shared text/utility class (e.g. `label`) is preferred over inline Tailwind; not required.

## Implementation Steps

1. In `app/reports/page.tsx`, locate the header `<div>` (lines 54–62) containing the `<h1>Отчёты</h1>` and the existing description `<p>`.
2. Ensure there is a small helper `<p>` immediately under the title that reads, in Russian, that reports can be reviewed and exported here. Suggested:
   ```tsx
   <p className="mt-1 text-xs text-slate-400">
     Здесь можно просматривать и экспортировать отчёты.
   </p>
   ```
3. Keep styling consistent with surrounding text (small, muted: `text-xs text-slate-400` matches the existing pattern). Place it after the existing description paragraph so the hierarchy reads: title → subtitle → helper hint.
4. Do not modify the API export routes or `src/reporting/*` — they are out of scope for a UI helper text.

## Validation Steps

- Run `npm run dev` (or the project's dev script) and open `/reports`; confirm the helper text appears under the title and renders correctly in Russian (no encoding/typo issues).
- Run `npm run lint` / `npm run build` (or `tsc`) to confirm no TSX/type regressions.
- Visually verify spacing/contrast on both empty and populated states (the header renders regardless of `runs` state).

## Risks

- **Duplication:** The text may already exist (lines 59–61). Adding another line risks redundant copy — confirm intended final wording before editing to avoid two near-identical hints.
- **Scope creep:** The provided "affected files" list is broad and misleading; touching export/reporting files would introduce unnecessary risk. Keep the change limited to `app/reports/page.tsx`.
- **Low risk overall:** Static, presentational text with no logic, data, or i18n framework involved.
