I have everything needed. The reference commit shows the exact pattern to follow.

# Implementation Plan

## Summary

Add a tiny Russian helper text line under the "Feedback Center" page title explaining that feedback improves future rankings. This mirrors the established pattern already applied to the reports page (commit `b074f9a`): a small `text-xs text-slate-400` paragraph appended inside the title header block. This is a single-file, presentation-only change.

## Files To Inspect

- `app/feedback/page.tsx` — already reviewed. The title block is lines 39–44 (`<div>` containing the `<h1>Feedback Center</h1>` and an existing English subtitle `<p>`). The new helper `<p>` goes immediately after the existing subtitle, still inside that wrapping `<div>`.

> Note: Of the 12 "Affected Files" listed, only `app/feedback/page.tsx` requires changes. The others (API routes, ranking logic, importers) are unrelated to a static UI text addition and should not be touched.

## Implementation Steps

1. In `app/feedback/page.tsx`, inside the header `<div>` (lines 39–44), after the existing `<p className="mt-1 text-sm text-slate-500">…</p>` (closing at line 43), add a new paragraph matching the reports-page convention:

   ```tsx
   <p className="mt-1 text-xs text-slate-400">
     Ваши оценки помогают улучшать будущие рейтинги статей.
   </p>
   ```

   - Use `text-xs text-slate-400` (smaller/lighter than the existing subtitle) and `mt-1` for consistent spacing — identical styling to the reports page helper text.
   - Keep the Russian copy short and focused on the "feedback improves future rankings" message.

## Validation Steps

1. `npx tsc --noEmit` (or the project's typecheck script) — confirm no type errors; this is a JSX-only change so it should pass cleanly.
2. Run the dev server (`npm run dev`) and open `/feedback`; confirm the new Russian line renders directly under the title, smaller and lighter than the English subtitle, with no layout shift.
3. Verify the Cyrillic text displays correctly (no mojibake) and spacing matches the reports page.

## Risks

- **Very low risk** — purely additive static markup, no logic, state, or data flow changes.
- **Language consistency**: the existing subtitle on this page is in English while the new line is Russian (matching the mixed-language state seen in recent commits). This is consistent with the requested pattern but leaves the page bilingual; flag if full-page translation is later desired.
