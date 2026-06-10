# Architecture Review

## Feature Request

Add a small Russian helper text under the sources page title explaining that RSS sources can be added and tested here

## Planner Input

# Implementation Plan

## Summary

Add a small Russian helper text beneath the "Источники" page title explaining that RSS sources can be added and tested on this page.

**Note:** This feature already appears to be implemented on the current branch (`agentic/rss-sources-helper-text`, commit `812e356`). The helper text exists at `app/sources/page.tsx:154-156`:

> «Здесь можно добавлять RSS-источники и проверять их доступность.»

This translates to "Here you can add RSS sources and check their availability." — which directly satisfies the request. The plan below documents the minimal change in case wording adjustment or re-implementation is desired.

## Files To Inspect

- `app/sources/page.tsx` — the only file requiring changes. The page title block is at lines 150–161; the existing helper `<p>` is at lines 154–156.

The remaining files in the affected list (API routes, collectors, importers) are **not relevant** to a static helper-text addition and require no changes.

## Implementation Steps

1. In `app/sources/page.tsx`, locate the title header block (around lines 150–157):
   - `<h1>Источники</h1>` (line 152)
   - subtitle `<p>RSS-ленты и Telegram-каналы.</p>` (line 153)
2. Ensure a small, muted helper paragraph sits directly under the title/subtitle:
   ```tsx
   <p className="mt-1 text-xs text-slate-400">
     Здесь можно добавлять RSS-источники и проверять их доступность.
   </p>
   ```
   - This is already present (lines 154–156). If only re-implementing, no edit is needed; if adjusting tone/wording, edit this single line.
3. Keep styling consistent with the existing subtitle — use a smaller, lighter class (`text-xs text-slate-400`) to visually distinguish it as a hint.

## Validation Steps

1. `npm run build` (or `next build`) / `npx tsc --noEmit` to confirm no type/JSX errors.
2. Run the dev server and navigate to `/sources`; confirm the Russian helper text renders under the title, above the "+ Новый источник" button, and that layout/wrapping is intact on mobile and desktop widths.
3. Lint check (`npm run lint`) if configured.

## Risks

- **Duplicate / redundant work** — the text already exists; re-adding it could create a duplicate paragraph. Verify current state before editing.
- **Minimal blast radius** — purely presentational JSX; no logic, API, or state changes, so risk is very low.
- **Wording/i18n consistency** — the page mixes Russian (titles, toasts) and English (form field labels like "Category", "Tags", "Save"). Ensure the helper text stays in Russian to match the surrounding title block.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/rss/sources/[id]/route.ts
- API route: app/api/rss/sources/route.ts
- API route: app/api/rss/collect/route.ts
- API route: app/api/rss/collections/[id]/route.ts
- API route: app/api/rss/collections/route.ts
- Other: app/rss/collections/page.tsx
- Other: src/collector/fetchFeeds.ts
- Other: app/sources/page.tsx
- Library/module: lib/rss/collect.ts
- Library/module: lib/rss/fetchFeed.ts
- Other: src/importers/parseRssTextFile.ts
- API route: app/api/feedback/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
