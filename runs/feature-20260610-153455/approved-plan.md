# Approved Plan

This is a small, well-scoped UI change. The relevant file is `app/sources/page.tsx`. Let me note the current header structure:

- **Line 152**: `<h1>` title — "Источники"
- **Line 153**: existing subtitle — `<p className="mt-1 text-sm text-slate-500">RSS-ленты и Telegram-каналы.</p>`

The page already has both an "Источник" add/edit editor (right panel) and a "Проверить" (test) button per source, so the helper text accurately describes existing functionality.

## Implementation Plan

**Goal:** Add a small Russian helper text under the sources page title explaining that RSS sources can be added and tested here.

**File to change:** `app/sources/page.tsx` (single file, one edit)

**Change:** Add one helper `<p>` element directly beneath the existing subtitle (line 153), inside the title `<div>` block (lines 151–154).

Proposed markup:
```tsx
<h1 className="text-2xl font-bold tracking-tight">Источники</h1>
<p className="mt-1 text-sm text-slate-500">RSS-ленты и Telegram-каналы.</p>
<p className="mt-1 text-xs text-slate-400">
  Здесь можно добавлять RSS-источники и проверять их доступность.
</p>
```

**Styling rationale:** Uses `text-xs text-slate-400` (one step lighter/smaller than the existing subtitle) so it reads as secondary helper text and matches the muted-hint styling already used elsewhere on the page (e.g. line 194). Reuses `mt-1` for consistent spacing.

**Why this is safe & minimal:**
- Pure additive, presentational change — no logic, state, API, or data flow touched.
- Confined to the existing header `<div>`; the sibling "+ Новый источник" button and its `flex items-center justify-between` layout are unaffected.
- Trivially reversible (delete one element).

**Out of scope:** None of the API routes, collectors, or other affected files listed in the task require changes — this is a presentation-only addition to the sources page header.

**Verification after implementation:** Visually confirm the helper line renders under the subtitle and the header row layout (title block left, button right) is unchanged.

I'm stopping here per plan-only mode — no files modified. Let me know if you'd like different wording or placement (e.g. replacing the existing subtitle rather than adding a second line).

