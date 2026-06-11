# Implementation Plan

## Summary

Task 002 translates the remaining global UI text to Russian, continuing the work from Task 001 (which translated the NavBar). Two surfaces are in scope:

1. **`app/layout.tsx`** — the page `metadata` (`title` and `description`), which currently read in English. `<html lang="ru">` is already set, so only the string values need translating.
2. **`components/Footer.tsx`** — the visible footer text: the `build` prefix and the environment badge label (`production`/`local`).

The listed API routes are *not* relevant to this task — they emit no user-facing UI copy related to layout metadata or the footer. They should be left untouched; the real targets are `app/layout.tsx` and `components/Footer.tsx`.

## Files To Inspect

- `app/layout.tsx` — `metadata.title` / `metadata.description` (lines 14–18).
- `components/Footer.tsx` — visible strings: `RSS Agent Lab v{...}`, the `APP_ENV` badge (line 15), and `build {BUILD_TIME}` (line 20).
- `lib/version.ts` — confirms `APP_ENV` resolves to `"production"` or `"local"` and is used both for display *and* for the conditional styling comparison (`APP_ENV === "production"`).
- `components/NavBar.tsx` — reference for the Task 001 translation style (inline Russian literals, no i18n framework).

## Implementation Steps

1. **`app/layout.tsx`** — translate the metadata values, keeping the product name "RSS Agent Lab" as-is:
   - `title`: e.g. `"RSS Agent Lab — Аналитика рынка"`.
   - `description`: e.g. `"Превращайте новостные RSS-ленты в аналитическую сводку TOP-N со ссылками на источники."`

2. **`components/Footer.tsx`** — translate visible labels without touching logic:
   - `build {BUILD_TIME}` → `сборка {BUILD_TIME}`.
   - Environment badge: do **not** change the `APP_ENV === "production"` comparison (used for styling). Instead, render a localized label derived from it — e.g. `APP_ENV === "production" ? "продакшн" : "локально"` (or map other values via a small lookup) — so the conditional class logic still works against the raw value.
   - Leave `RSS Agent Lab v{APP_VERSION}` unchanged (product name + version).

3. Keep the no-framework, inline-literal approach consistent with Task 001 (NavBar). Do not introduce an i18n library.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck script) to confirm no type regressions.
- `npm run build` / `next build` to confirm the layout and Footer compile.
- Run the app and visually confirm: browser tab title shows the Russian `title`, and the footer shows `сборка …` and the translated environment badge.
- Confirm the environment badge still shows the green "production" styling when `APP_ENV === "production"` (styling logic must remain tied to the raw value, not the translated label).

## Risks

- **Behavioral coupling on `APP_ENV`**: translating the displayed value directly would break the `=== "production"` style check. Mitigation: translate only a derived display label, keep the comparison on the raw value.
- **Scope confusion**: the task's "Affected Files" list is API routes, which don't match the task title. Translating those would be incorrect; the actual targets are `app/layout.tsx` and `components/Footer.tsx`.
- **Wording consistency**: Russian phrasing should match tone/terminology already chosen in Task 001 (NavBar) and the reports page; minor copy-review may be wanted.
- **Untranslatable identifiers**: product name "RSS Agent Lab" and version/build values are intentionally left in their original form.
