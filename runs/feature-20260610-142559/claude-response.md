# Claude Response

I've located the relevant code. The RSS preview UI lives in `components/PreviewPanel.tsx`, and the "✨ AI summaries" button (lines 100–108) triggers an opt-in call to `/api/rss/summarize`. The summarize route itself already documents this as opt-in. No note currently tells the user the AI summaries are optional.

Here's my plan.

## Implementation Plan: Note that AI summaries are optional

### Goal
Add a small, unobtrusive note in the RSS preview clarifying that AI summaries are optional (only generated when the user clicks the button), without changing any behavior.

### Scope
- **One file only:** `components/PreviewPanel.tsx`
- No API, schema, auth, or config changes. The `/api/rss/summarize` route is already opt-in (Claude is only called on button click) — purely a UI copy addition.

### Change

In `components/PreviewPanel.tsx`, inside the preview card header block (the `div` at lines 99–108 containing the `<h3>` "Первые N новостей" and the AI summaries button), add a short helper line directly beneath that header row.

**Proposed snippet** (placed right after the closing `</div>` of the header flex row, line 108, before the `summaryError` block):

```tsx
<p className="mb-3 text-xs text-slate-400">
  AI-описания опциональны — нажмите «✨ AI summaries», чтобы сгенерировать их для
  первых {preview.previewArticles.length} новостей.
</p>
```

Rationale for placement and wording:
- Sits between the button and the article list, so it reads as context for the button.
- Uses the existing muted text style (`text-xs text-slate-400`) already used elsewhere in the component for secondary text, keeping it visually small/non-intrusive.
- Russian copy matches the surrounding UI language (rest of the panel is in Russian: "Разобрано", "Первые N новостей", "Источники", "Ключевые слова").
- Reuses `preview.previewArticles.length` to stay consistent with the heading and the actual sample size.

### Why this is the smallest safe change
- Pure additive JSX (one `<p>`); no state, props, handlers, or logic touched.
- Trivially reversible (delete the element).
- No new imports or dependencies.

### Verification
- Visual check: load the preview after an upload/collect; confirm the note appears under the header and above the list, and that clicking "✨ AI summaries" still works unchanged.
- `npm run lint` / build to confirm no TSX errors (no type changes expected).

### Open question (minor)
- **Language:** I assumed Russian to match the panel's existing copy. If you'd prefer English (the headers/eyebrows like "Preview · No LLM yet" are in English), I can swap the wording — let me know your preference.

Awaiting your go-ahead before making any edits.

