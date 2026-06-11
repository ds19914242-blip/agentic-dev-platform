# Implementation Plan

## Summary

Add a single small Russian helper paragraph beneath the title in the Feedback page header, explaining that feedback improves future rankings. This is a presentation-only change isolated to `app/feedback/page.tsx`, mirroring the existing reports-page pattern (`app/reports/page.tsx:59-61`). None of the API routes, ranking logic, or other "affected files" need changes — they appear in the request only as repository context.

## Files To Inspect

- `app/feedback/page.tsx` — target file; header block is at lines 39–44.
- `app/reports/page.tsx` (lines 54–62) — reference for the established "tiny helper text" styling: `<p className="mt-1 text-xs text-slate-400">…</p>`.

## Implementation Steps

1. In `app/feedback/page.tsx`, inside the header `<div>` (lines 39–44), add a new `<p>` after the existing subtitle paragraph (line 41–43):
   ```tsx
   <p className="mt-1 text-xs text-slate-400">
     Каждый ваш отзыв помогает точнее ранжировать новости в будущих отчётах.
   </p>
   ```
   - Use `text-xs text-slate-400` (the smaller/lighter "tiny" tier) to distinguish it from the existing `text-sm text-slate-500` subtitle, exactly as the reports page does.
   - Keep it as plain static JSX — no new state, props, or imports.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck script) — confirm no type errors; this change is JSX-only so it should pass.
- Run the dev server and open `/feedback`; verify the new helper line renders directly under "Feedback Center" subtitle, smaller and lighter than the line above it.
- Confirm no layout shift to the KpiCard grid below.

## Risks

- Minimal — purely additive, static UI text in one file.
- Minor consistency note: surrounding feedback-page chrome ("Feedback Center", "Relevant", etc.) is in English while the new text is Russian, matching the repo's in-progress English→Russian localization direction (see recent commits). Confirm Russian is the intended language for this string before merging.
