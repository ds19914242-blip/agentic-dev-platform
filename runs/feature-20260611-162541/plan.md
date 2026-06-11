No i18n framework exists in this repo — the recent "Translate …" commits are direct string replacements in source. The NavBar currently holds hardcoded Russian labels, and this task translates them to English (matching the epic's translation effort).

Note: the "Affected Files" list (API routes) is irrelevant to this task — they contain no UI navigation strings. The only file that needs changing is `components/NavBar.tsx`.

# Implementation Plan

## Summary

Translate the user-facing navigation strings in `components/NavBar.tsx` from Russian to English. This is a pure, isolated string-replacement task: the `LINKS` array labels, plus the "Выйти" (logout) button text. No routing, hrefs, logic, or styling changes — only display text.

## Files To Inspect

- `components/NavBar.tsx` — the only file with NavBar nav links (the `LINKS` array, lines 6–16, and the logout button, line 66). hrefs must stay unchanged.
- `app/layout.tsx` — confirm where `NavBar` is rendered and that `<html lang>` is set appropriately (optional; may update `lang="ru"` → `lang="en"` if present).
- Sibling already-translated components (e.g. `Footer.tsx`) — to match tone/terminology consistency with the rest of the epic.

## Implementation Steps

1. In `components/NavBar.tsx`, translate the `LINKS` array labels (keep `href` values identical):
   - Панель → Dashboard
   - Источники → Sources
   - Коллекции → Collections
   - Запуск анализа → Run Analysis
   - Отчёты → Reports
   - Шаблоны → Templates
   - Обратная связь → Feedback
   - Список чтения → Reading List
   - Настройки → Settings
2. Translate the logout button text "Выйти" → "Log out" (line 66).
3. Leave the brand label "RSS Agent Lab", the `EXACT` set, `href`s, and all class names untouched.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck) — confirm no type breakage.
- `npm run lint` if configured.
- `npm run build` / `npm run dev` and visually confirm the nav bar renders the English labels and active-link highlighting still works on each route.
- Grep `components/NavBar.tsx` for remaining Cyrillic characters to ensure none were missed.

## Risks

- **Low risk overall** — display-string-only change.
- Accidentally editing an `href` while changing a label would break navigation; verify hrefs are byte-identical after the edit.
- Terminology drift across the translation epic (e.g. "Run Analysis" vs "Analyze") — align wording with already-translated pages for consistency.
- The provided "Affected Files" list is misleading (API routes); do not modify them.
