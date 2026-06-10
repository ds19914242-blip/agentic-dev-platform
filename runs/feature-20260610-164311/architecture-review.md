# Architecture Review

## Feature Request

Translate only the reports page visible UI text to Russian.

## Planner Input

# Implementation Plan

## Summary

Translate all visible UI text on the reports page (`app/reports/page.tsx`) from English to Russian. This is a self-contained, single-file change touching only hard-coded display strings — no logic, data, or API changes. The listed API routes are not relevant to this feature and require no edits (they emit no reports-page UI text). A Russian helper paragraph already exists on the page (line 60) from a prior commit and needs no change.

## Files To Inspect

- `app/reports/page.tsx` — the only file with strings to translate (already read).
- `components/ConfirmModal.tsx` — confirm it renders the `title`/`message`/button labels as passed-in props (so translating the props on the reports page is sufficient and modal buttons like "Confirm/Cancel" are out of scope unless they live here as defaults).
- `components/Toast.tsx` — confirm `toast(message, variant)` simply displays the passed string (so translating the message argument is sufficient).

## Implementation Steps

Edit `app/reports/page.tsx`, replacing each English UI string with a Russian equivalent. Do **not** translate data-derived values (e.g. `{r.mode}`, `{r.filename}`, `{r.profileName}`) or the existing Russian helper line.

Strings to translate:

| Line | English | Suggested Russian |
|------|---------|-------------------|
| 39 | `Report deleted` | `Отчёт удалён` |
| 41 | `Failed to delete` | `Не удалось удалить` |
| 55 | `Reports` | `Отчёты` |
| 57 | `Saved analyses — open without re-running Claude.` | `Сохранённые анализы — открывайте без повторного запуска Claude.` |
| 68 | placeholder `Search by file…` | `Поиск по файлу…` |
| 76 | `All modes` | `Все режимы` |
| 77 | `Fast` | `Быстрый` |
| 78 | `Balanced` | `Сбалансированный` |
| 79 | `Deep` | `Глубокий` |
| 92 | `No reports yet.` / `Nothing matches your filters.` | `Отчётов пока нет.` / `Ничего не найдено по фильтрам.` |
| 95 | `Run analysis` | `Запустить анализ` |
| 121 | label `Selected` | `Отобрано` |
| 125 | label `Trends` | `Тренды` |
| 130 | `Open` | `Открыть` |
| 133/136 | `PDF` / `MD` | leave as-is (format names) |
| 142 | `Delete` | `Удалить` |
| 152 | modal `title` `Delete report?` | `Удалить отчёт?` |
| 153 | modal `message` | `Отчёт, загруженный файл и запись в истории будут удалены. Это действие необратимо.` |

Note: the `<option>` `value` attributes (`all`/`fast`/`balanced`/`deep`) and the `modeFilter` state values must stay unchanged — only the visible option labels change.

## Validation Steps

1. `npx tsc --noEmit` (or project's typecheck script) — ensure no type/syntax breakage.
2. Run lint if configured (`npm run lint`).
3. Start the dev server and open `/reports`; visually confirm all labels, filter options, empty-state text, card labels, buttons, toast messages, and the delete-confirmation modal render in Russian, and that mode filtering still works (option values unchanged).

## Risks

- **Out-of-scope creep**: the many API routes in "Affected Files" tempt edits; they contain no reports-page UI text — leave untouched.
- **Breaking filter logic**: accidentally changing `<option value>` attributes or state literals would break mode filtering. Translate labels only.
- **Modal/Toast button text**: "Confirm"/"Cancel" buttons may have English defaults inside `ConfirmModal.tsx`; decide whether they fall within "reports page visible text." Recommend confirming during inspection — translating them touches a shared component used by other pages, which exceeds the stated scope.
- **Encoding**: ensure file stays UTF-8 so Cyrillic renders correctly.


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
