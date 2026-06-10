# Architecture Review

## Feature Request

Translate only the reports page visible UI text to Russian. Change only app/reports/page.tsx.

## Planner Input

# Implementation Plan

## Summary

Translate all user-visible English UI strings in `app/reports/page.tsx` to Russian. The file is a client component that already has one Russian helper line; all remaining English text (title, subtitle, search/filter controls, empty states, card labels, action buttons, toasts, and the delete confirmation modal) needs translation. No other files change. The Russian date formatting (`toLocaleString("ru-RU")`) is already in place and stays as-is.

## Files To Inspect

- `app/reports/page.tsx` — the only file to edit (already read; full contents understood).
- `components/ConfirmModal.tsx` — read-only check to confirm `title`/`message` props are rendered as plain text (so translated strings display correctly); do not modify.
- `components/Toast.tsx` — read-only check that `toast(message, variant)` takes a free-text message; do not modify.

## Implementation Steps

Replace each visible string literal in `app/reports/page.tsx` with a Russian equivalent. Leave logic, class names, `r.mode` raw value display, and `"ru-RU"` formatting untouched.

1. Header (lines 55–58): `"Reports"` → `"Отчёты"`; subtitle `"Saved analyses — open without re-running Claude."` → e.g. `"Сохранённые анализы — открывайте без повторного запуска Claude."`. (Line 60 Russian helper text already present — keep.)
2. Search input placeholder (line 68): `"Search by file…"` → `"Поиск по файлу…"`.
3. Mode filter options (lines 76–79): `"All modes"` → `"Все режимы"`, `"Fast"` → `"Быстрый"`, `"Balanced"` → `"Сбалансированный"`, `"Deep"` → `"Глубокий"`. (Keep the `value` attributes unchanged — they are logic keys.)
4. Empty states (line 92): `"No reports yet."` → `"Отчётов пока нет."`; `"Nothing matches your filters."` → `"Ничего не найдено по вашим фильтрам."`.
5. Empty-state CTA (line 96): `"Run analysis"` → `"Запустить анализ"`.
6. Card labels: `"Selected"` (line 121) → `"Отобрано"`; `"Trends"` (line 125) → `"Тренды"`.
7. Card actions: `"Open"` (line 130) → `"Открыть"`; `"Delete"` (line 142) → `"Удалить"`. Leave `"PDF"` and `"MD"` as-is (format names).
8. Toasts (lines 39, 41): `"Report deleted"` → `"Отчёт удалён"`; `"Failed to delete"` → `"Не удалось удалить"`.
9. ConfirmModal props (lines 152–153): `title="Delete report?"` → `"Удалить отчёт?"`; `message="The report, upload, and history record will be removed. This cannot be undone."` → `"Отчёт, загрузка и запись в истории будут удалены. Это действие необратимо."`.

Note: the `r.mode` badge (line 106) renders the raw mode key (`fast`/`balanced`/`deep`) and is data, not a UI label — leave it unless the requester wants badge text localized (out of scope for "visible UI text" minimal change; flag as optional).

## Validation Steps

- `npx tsc --noEmit` (or project typecheck script) — confirm no type/JSX breakage from the string edits.
- `npm run lint` if configured.
- `npm run dev` and open `/reports`: verify title, controls, empty state, card labels/buttons, delete toast, and confirm modal all render in Russian; confirm filtering and delete still work (logic keys unchanged).

## Risks

- **Low overall** — purely string substitution in one file.
- Accidentally translating a non-display value (e.g. a `<option value=...>` key or the `r.mode` badge) would break filtering; keep `value` attributes English.
- Cyrillic in JSX must remain inside the existing quotes/braces; ensure no stray unescaped characters break the literal.
- Ensure the file's source encoding stays UTF-8 so Cyrillic renders correctly.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Other: app/reports/page.tsx
- Other: src/importers/parseRssTextFile.ts
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts
- API route: app/api/health/route.ts
- API route: app/api/jobs/[jobId]/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
