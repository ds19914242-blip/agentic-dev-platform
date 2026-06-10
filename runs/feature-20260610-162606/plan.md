I have enough to produce the plan. Note: the "Affected Files" list (API routes) is irrelevant to this request — API routes contain no user-facing UI. The actual surface is `app/page.tsx` and the components it renders.

# Implementation Plan

## Summary

Translate the home page (`app/page.tsx`) and its directly-rendered components to Russian. Prior commits already translated parts (error/preview/upload-busy strings, ModeSelector headings, ErrorState), so this is a finish-the-job pass: convert the remaining English UI strings — chiefly `Hero`, `SourcePicker`, the inline RSS-collection block in `page.tsx`, and the English mode/button labels. Translate only human-visible text; leave code identifiers, `PerformanceMode` ids (`fast`/`balanced`/`deep`), CSS classes, and API payload keys untouched.

## Files To Inspect

- `app/page.tsx` — inline RSS block + action buttons (mix of EN/RU).
- `components/Hero.tsx` — fully English.
- `components/SourcePicker.tsx` — English source labels.
- `components/ModeSelector.tsx` — English `label` values (`Fast`/`Balanced`/`Deep`).
- `components/UploadDropzone.tsx` — already RU (verify, no change expected).
- `components/ErrorState.tsx` — already RU (verify).
- Rendered but not yet read — audit each for English strings: `components/PreviewPanel.tsx`, `components/ProfileSelector.tsx`, `components/TopicSelector.tsx`, `components/ProgressTimeline.tsx`, `components/Dashboard.tsx`.

## Implementation Steps

1. **Hero.tsx** — translate eyebrow ("Intelligence Platform"), the H1 ("Turn raw feeds into / market intelligence"), and the subtext paragraph. Preserve the `<br/>` and `gradient-text` span structure.
2. **SourcePicker.tsx** — translate labels: `Upload TXT file` → e.g. "Загрузить TXT-файл"; `RSS Collection` → "RSS-коллекция". Keep `id` values `txt`/`rss` and glyphs.
3. **page.tsx inline RSS block** (lines ~211–243) — translate: `RSS collection` label, the "No collections yet — create one and add sources first." sentence (keep the `/rss/collections` link), `Choose a collection…`, the `({c.sourceIds.length} sources)` suffix, `Collecting articles…`, `Collect Articles →`.
4. **page.tsx action button** — `Run Analysis →` → "Запустить анализ →". (Buttons "← Другой файл", "← Новый анализ", warnings, and fallback `error` strings are already Russian — leave them.)
5. **ModeSelector.tsx** — translate the `label` fields (`Fast`/`Balanced`/`Deep`) to Russian; captions/headings already Russian.
6. **Audit remaining rendered components** (PreviewPanel, ProfileSelector, TopicSelector, ProgressTimeline, Dashboard) and translate any English user-facing strings found, following the same rules.
7. **Consistency pass** — ensure terminology matches already-translated pages (use the same words for "анализ", "темы", "коллекция" as in sources/reports pages translated in recent commits).

## Validation Steps

- `npm run build` (or `next build`) / `tsc --noEmit` — confirm no type/JSX breakage from edits.
- `grep -nE '[A-Za-z]{4,}' ` across edited components to spot any leftover English UI text (ignoring class names, ids, props).
- Run the dev server and walk the home-page phases — empty (Hero + SourcePicker + dropzone/RSS), preview (selectors + buttons), running, done, error — visually confirming Russian throughout.

## Risks

- **Over-translation**: accidentally changing `PerformanceMode` ids, `sourceType` values, CSS class strings, or API JSON keys would break logic — translate display text only.
- **Hidden English in deeper components** (Dashboard, TopicSelector, ProgressTimeline) may be larger than expected; scope could grow. Flag if a component is extensive.
- **Terminology drift** vs. previously translated pages — pick consistent wording.
- **Layout shift**: longer Russian strings may wrap differently in fixed-width buttons/cards; spot-check the responsive layout.
- The provided "Affected Files" list is misleading (API routes carry no UI) — following it literally would miss the real files.
