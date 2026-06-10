# Implementation Plan

## Summary

Translate the visible navigation link labels in the top NavBar from English to Russian. The component is `components/NavBar.tsx`, where a `LINKS` array holds nine `{ href, label }` entries rendered as nav links. Only the `label` strings need translation — `href` routes must stay unchanged. The logout button is already Russian (`Выйти`), and the brand name "RSS Agent Lab" is a product name typically left as-is.

Note: The "Affected Files" list (API routes) is not relevant to this task — none render NavBar labels. The single file that owns the navigation links is `components/NavBar.tsx`.

## Files To Inspect

- `components/NavBar.tsx` — owns the `LINKS` array (lines 6–16) and renders `l.label`. **Primary and only file to edit.**
- (Optional, for terminology consistency) `app/reports/page.tsx`, `app/sources/page.tsx`, `app/collections/page.tsx` — to match wording already used on the destination pages, since prior commits translated some pages to Russian.

## Implementation Steps

1. In `components/NavBar.tsx`, update each `label` in the `LINKS` array to its Russian equivalent, leaving every `href` untouched. Suggested translations:
   - `Dashboard` → `Дашборд` (or `Панель`)
   - `Sources` → `Источники`
   - `Collections` → `Коллекции`
   - `Run Analysis` → `Анализ` (or `Запустить анализ`)
   - `Reports` → `Отчёты`
   - `Templates` → `Шаблоны`
   - `Feedback` → `Обратная связь`
   - `Reading List` → `Список чтения`
   - `Settings` → `Настройки`
2. Leave the brand label "RSS Agent Lab", the `EXACT` set, and the already-Russian `Выйти` button as-is.
3. Confirm wording matches the headings on the corresponding translated pages for consistency.

## Validation Steps

- Run the type/lint/build check (e.g. `npm run build` or `npm run lint`) to confirm no syntax breakage.
- Manually load the app and verify the nav renders the Russian labels, active-link highlighting still works, and each link routes to the correct page (hrefs unchanged).
- Verify the layout doesn't overflow on the `lg` breakpoint where the nav is shown, since some Russian words are longer (e.g. "Обратная связь").

## Risks

- **Longer strings**: Russian labels can be wider than English; the horizontal nav (`flex-wrap`, `gap-1`) may wrap or crowd on mid-width screens. Prefer concise variants (e.g. `Анализ`) where reasonable.
- **Terminology drift**: If destination pages use different wording, nav labels could feel inconsistent — align with existing translated pages.
- **Scope mismatch**: The provided "Affected Files" list points at API routes, not the UI. Editing those would be wrong; the change belongs solely in `components/NavBar.tsx`.
