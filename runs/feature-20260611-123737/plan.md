The task title ("Translate NavBar navigation links") matches `components/NavBar.tsx`, which has English link labels and an already-Russian logout button (`Выйти`). The listed API routes are not relevant to this UI translation. Here's the plan.

# Implementation Plan

## Summary

Translate the visible navigation link labels in `components/NavBar.tsx` from English to Russian, matching the project's existing Russian-translation pattern (the logout button is already `Выйти`, and reports/feedback pages were recently translated). Only the user-facing `label` strings change; `href` routes, the brand name, and component logic stay untouched.

## Files To Inspect

- `components/NavBar.tsx` — the only file requiring edits (the `LINKS` array, lines 6–16).
- `app/reports/page.tsx` / `app/feedback/page.tsx` — recently translated pages; skim to match tone/terminology and keep wording consistent.
- The API routes in the epic's "Affected Files" list are **not** relevant to this task and require no changes.

## Implementation Steps

1. In `components/NavBar.tsx`, update each `label` in the `LINKS` array to its Russian equivalent, keeping every `href` exactly as-is:
   - `Dashboard` → `Дашборд` (or `Панель`)
   - `Sources` → `Источники`
   - `Collections` → `Коллекции`
   - `Run Analysis` → `Запустить анализ`
   - `Reports` → `Отчёты`
   - `Templates` → `Шаблоны`
   - `Feedback` → `Обратная связь`
   - `Reading List` → `Список чтения`
   - `Settings` → `Настройки`
2. Leave the brand text `RSS Agent Lab` (line 39), all `href` values, the `EXACT` set, and the `Выйти` button unchanged.
3. Do not alter routing, active-state logic, or class names.

## Validation Steps

- Run `npm run build` (or `tsc --noEmit`) to confirm no type/compile errors — changes are string-only, so this should be clean.
- Run the dev server and visually confirm the nav renders the Russian labels and that active-link highlighting still works on each route.
- Verify the wording is consistent with already-translated pages (Reports, Feedback).

## Risks

- **Low overall risk** — only display strings change; routes and logic are untouched.
- **Terminology consistency**: ensure chosen Russian terms match those already used elsewhere in the app (e.g., how "Reports"/"Feedback" are phrased on their pages) to avoid mismatched vocabulary.
- **Scope creep**: the epic lists many unrelated API files; editing them is out of scope and would be a mistake. Confine changes to `NavBar.tsx`.
