# Claude Implementation Response

Done. `npx tsc --noEmit` passed with no errors.

## Changed files
- **`components/PreviewPanel.tsx`** — Added a single muted helper `<p>` between the preview card header (with the "✨ AI summaries" button) and the article list, clarifying that AI summaries are optional and only generated on button click. Uses the existing `text-xs text-slate-400` style and reuses `preview.previewArticles.length` for the count.

## Risks
- **None functional.** Pure additive JSX — no state, props, handlers, or logic touched, no new imports. Trivially reversible.
- **Cosmetic only:** the note sits above the list; if a different placement or English wording is preferred, it's a one-line swap. (Per the plan's open question, I used Russian to match the panel's surrounding copy.)
