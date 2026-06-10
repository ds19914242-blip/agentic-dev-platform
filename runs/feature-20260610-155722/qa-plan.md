# QA Plan

## Feature Request

Add a small Russian helper text under the sources page title explaining that RSS sources can be added and tested here

## Based On Plan

# Implementation Plan

## Summary

Add a small Russian helper text beneath the "Источники" page title explaining that RSS sources can be added and tested on this page.

**Important finding:** This feature appears to be **already implemented**. `app/sources/page.tsx:154-156` already contains a helper text matching this exact request, and the most recent commit (`812e356 Add RSS sources helper text`) corresponds to it:

```tsx
<p className="mt-1 text-xs text-slate-400">
  Здесь можно добавлять RSS-источники и проверять их доступность.
</p>
```

The plan below assumes the goal is either (a) verifying/confirming the existing text, or (b) refining its exact wording. No new structural work is required.

## Files To Inspect

- `app/sources/page.tsx` — the only file requiring changes. The title block is at lines 150–157 (`<h1>Источники</h1>`, subtitle `<p>`, and the existing helper `<p>`). All other "Affected Files" (API routes, collectors, parsers) are unrelated to a static UI text change and can be ignored.

## Implementation Steps

1. Confirm with the requester whether the existing helper text at `app/sources/page.tsx:154-156` already satisfies the request.
2. If new wording is desired, edit the existing `<p className="mt-1 text-xs text-slate-400">` element in place (do not add a duplicate). Suggested text emphasizing both add + test:
   - `Здесь можно добавлять RSS-источники и проверять их доступность.`
3. Keep styling consistent with the adjacent subtitle (`text-xs text-slate-400`, `mt-1`) so it sits visually under the title without disrupting the flex layout in the header (`lines 150–157`).
4. Do not alter the `+ Новый источник` button or the editor panel.

## Validation Steps

1. `npm run lint` / `npm run build` (or `npx tsc --noEmit`) to confirm no JSX/TypeScript errors.
2. Run the app and navigate to `/sources`; verify the helper text renders directly under the title, on one line on desktop, and wraps gracefully on narrow widths without overlapping the button.
3. Confirm there is exactly one helper paragraph (no accidental duplicate alongside the existing one).

## Risks

- **Duplication risk:** Since the text already exists, a naive "add" would create two near-identical paragraphs. Edit in place instead.
- **Layout shift:** The header uses `flex items-center justify-between`; an extra long line of text could push against the button on small screens. The existing `text-xs` styling already mitigates this.
- **Localization consistency:** Surrounding form labels mix Russian and English (e.g., "Category", "Tags", "Active"). The helper text should remain Russian per the request; no broader translation work is in scope.


## Based On Architecture Review

# Architecture Review

## Feature Request

Add a small Russian helper text under the sources page title explaining that RSS sources can be added and tested here

## Planner Input

# Implementation Plan

## Summary

Add a small Russian helper text beneath the "Источники" page title explaining that RSS sources can be added and tested on this page.

**Important finding:** This feature appears to be **already implemented**. `app/sources/page.tsx:154-156` already contains a helper text matching this exact request, and the most recent commit (`812e356 Add RSS sources helper text`) corresponds to it:

```tsx
<p className="mt-1 text-xs text-slate-400">
  Здесь можно добавлять RSS-источники и проверять их доступность.
</p>
```

The plan below assumes the goal is either (a) verifying/confirming the existing text, or (b) refining its exact wording. No new structural work is required.

## Files To Inspect

- `app/sources/page.tsx` — the only file requiring changes. The title block is at lines 150–157 (`<h1>Источники</h1>`, subtitle `<p>`, and the existing helper `<p>`). All other "Affected Files" (API routes, collectors, parsers) are unrelated to a static UI text change and can be ignored.

## Implementation Steps

1. Confirm with the requester whether the existing helper text at `app/sources/page.tsx:154-156` already satisfies the request.
2. If new wording is desired, edit the existing `<p className="mt-1 text-xs text-slate-400">` element in place (do not add a duplicate). Suggested text emphasizing both add + test:
   - `Здесь можно добавлять RSS-источники и проверять их доступность.`
3. Keep styling consistent with the adjacent subtitle (`text-xs text-slate-400`, `mt-1`) so it sits visually under the title without disrupting the flex layout in the header (`lines 150–157`).
4. Do not alter the `+ Новый источник` button or the editor panel.

## Validation Steps

1. `npm run lint` / `npm run build` (or `npx tsc --noEmit`) to confirm no JSX/TypeScript errors.
2. Run the app and navigate to `/sources`; verify the helper text renders directly under the title, on one line on desktop, and wraps gracefully on narrow widths without overlapping the button.
3. Confirm there is exactly one helper paragraph (no accidental duplicate alongside the existing one).

## Risks

- **Duplication risk:** Since the text already exists, a naive "add" would create two near-identical paragraphs. Edit in place instead.
- **Layout shift:** The header uses `flex items-center justify-between`; an extra long line of text could push against the button on small screens. The existing `text-xs` styling already mitigates this.
- **Localization consistency:** Surrounding form labels mix Russian and English (e.g., "Category", "Tags", "Active"). The helper text should remain Russian per the request; no broader translation work is in scope.


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


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/rss/collections/page.tsx
- src/collector/fetchFeeds.ts
- app/sources/page.tsx
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/importers/parseRssTextFile.ts
- app/api/feedback/route.ts

## Required Command

```bash
npx tsc --noEmit
```