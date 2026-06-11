# Claude Implementation Response

The chip classes exist. Implementation complete.

## Summary of changes

**`components/Dashboard.tsx`** (only file modified):
- Added `useMemo`/`useState` imports.
- Added a local `hostname()` helper mirroring `NewsCard.tsx` exactly (`www.` stripped, empty string on parse failure) plus a `NO_SOURCE` sentinel (`"без источника"`).
- Added `domain` filter state (`null` = all sources).
- Pre-computed `rankedTopNews`/`rankedPotential` that tag each article with its **unfiltered** 1-based rank, so `#N` stays stable when a filter is active.
- Derived a de-duplicated, ru-sorted `domains` list with per-domain counts from the canonical TOP list.
- Rendered a chip row (`Все источники` + one chip per `domain (count)`) under the "ТОП-N новостей" heading, only when ≥2 distinct domains exist, using the existing `chip`/`chip-on`/`chip-off` classes.
- Filtered both the TOP and Potentially-Relevant grids by the selected domain; both now show a filter-aware empty-state message ("Нет новостей для выбранного источника"), while the TOP grid keeps the original "проверьте формат файла" message when the report itself is empty.
- Charts/stats/analytics untouched — they remain full-report figures.

No prop/signature changes to `Dashboard` or `NewsCard`. No `app/api/**`, schema, or config changes.

## Verification
- `npx tsc --noEmit` → passes, no errors.
- Confirmed `chip`/`chip-on`/`chip-off` classes exist in `app/globals.css`.

## Risks
- **Low.** Pure client-side UI change in one component, fully reversible.
- **Hostname duplication:** the helper is a 5th copy of `hostname()`. Behavior matches `NewsCard` so filter chips and card labels stay consistent, but a future change to one copy must be mirrored. (Plan flagged a shared `lib/hostname.ts` as an optional follow-up.)
- **`key` change:** list keys switched from array index to `rank`. Ranks are unique within each list, so this is safe and actually more stable than index keys under filtering.
- **Manual UI not exercised:** I didn't run the app. Suggested manual check — open a saved report with articles from ≥2 domains and confirm chips appear, selection narrows both grids, ranks stay stable, and "Все источники" restores the full list.
