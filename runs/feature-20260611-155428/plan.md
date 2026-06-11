# Implementation Plan

## Summary

Translate the remaining visible UI text in `components/StrategicSignals.tsx` to Russian, consistent with the prior translation tasks (e.g., NavBar). The section heading (`Стратегические сигналы`) is **already** translated. The only English UI strings left are the five category group **names** rendered in the card headers. These are static display labels — translate them in place. The `items` values come from analysis data (`trends.strategicSignals.*`) and the `icon` symbols are not translatable text, so neither is touched.

## Files To Inspect

- `components/StrategicSignals.tsx` — the only file requiring edits; the `groups` array (lines 4–10) holds the English labels.
- `src/types/report.ts` — confirm `TrendAnalysis.strategicSignals` field names (`productLaunches`, `partnershipsIntegrations`, `aiInitiatives`, `iamGovernance`, `secOpsPlatform`) so the `name` change does not affect the `key={g.name}` / data wiring.
- `components/NavBar.tsx` (reference, already read) — established Russian translation tone/pattern.

> Note: The many `app/api/**/route.ts` files in "Affected Files" contain no user-facing UI copy and are out of scope for this UI-translation task. No changes there.

## Implementation Steps

1. In `components/StrategicSignals.tsx`, translate the five `name` strings in the `groups` array:
   - `"Product Launches"` → `"Запуск продуктов"`
   - `"Partnerships"` → `"Партнёрства"`
   - `"AI Initiatives"` → `"ИИ-инициативы"`
   - `"IAM / Governance"` → `"IAM / Управление"`
   - `"SecOps / Platform"` → `"SecOps / Платформа"`
2. Leave `icon`, `items`, the already-translated `<h2>` heading, and the empty-state `—` placeholder unchanged.
3. Confirm `key={g.name}` still yields unique keys after translation (the five new strings are all distinct — no collision).

## Validation Steps

- Run the type checker / build (`npm run build` or `tsc --noEmit` per repo config) to confirm no type or JSX errors.
- Visually verify (or grep) that no English UI string remains in `components/StrategicSignals.tsx`.
- Confirm only `components/StrategicSignals.tsx` appears in `git diff`.

## Risks

- **Very low risk** — change is limited to display-label string literals; no logic, data bindings, or props change.
- The `name` field also serves as a React `key`; translated strings remain unique, so rendering is unaffected.
- Translation wording/casing should match the project's existing Russian tone; the suggested terms keep widely-recognized acronyms (IAM, SecOps, ИИ) intact, consistent with typical Russian tech UI conventions.
