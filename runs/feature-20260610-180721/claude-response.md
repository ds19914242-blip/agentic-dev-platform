# Claude Response

I have everything I need. Here's my analysis and plan.

## Findings

- **The real file is `components/NavBar.tsx`** — none of the 12 listed API routes contain navigation links, so they are not touched by this task. I'm flagging that mismatch rather than editing unrelated files.
- The nav link labels in `LINKS` (`NavBar.tsx:6-16`) are still English, even though the app is mid-translation to Russian — the logout button already reads `"Выйти"` (line 66) and pages like Reports/Sources are translated.
- Other pages (dashboard, collections, feedback, settings, reading-list) are still English, but **the task scope is only the NavBar links** — I won't touch page bodies (smallest safe change).
- Verified terminology against already-translated pages: `Отчёты` (reports/page.tsx:55), `Источники` (sources/page.tsx:152), `Запустить анализ` (reports/page.tsx:95).

## Implementation Plan

**Single file:** `components/NavBar.tsx` — translate only the `label` values in the `LINKS` array (lines 6–16). The `href` values, `EXACT` set, brand name "RSS Agent Lab", and all logic stay untouched.

| Line | href | Current label | → Russian |
|------|------|---------------|-----------|
| 7 | `/dashboard` | Dashboard | Дашборд |
| 8 | `/sources` | Sources | Источники |
| 9 | `/collections` | Collections | Коллекции |
| 10 | `/` | Run Analysis | Запустить анализ |
| 11 | `/reports` | Reports | Отчёты |
| 12 | `/templates` | Templates | Шаблоны |
| 13 | `/feedback` | Feedback | Обратная связь |
| 14 | `/reading-list` | Reading List | Список чтения |
| 15 | `/settings` | Settings | Настройки |

**Exact diff (the only change):**
```tsx
const LINKS = [
  { href: "/dashboard", label: "Дашборд" },
  { href: "/sources", label: "Источники" },
  { href: "/collections", label: "Коллекции" },
  { href: "/", label: "Запустить анализ" },
  { href: "/reports", label: "Отчёты" },
  { href: "/templates", label: "Шаблоны" },
  { href: "/feedback", label: "Обратная связь" },
  { href: "/reading-list", label: "Список чтения" },
  { href: "/settings", label: "Настройки" },
];
```

**Why this is safe & minimal**
- Pure string changes to display labels; no routing, state, or styling touched.
- Fully reversible (one array).
- No auth, billing, secrets, DB, or deploy config involved.
- `<html lang="ru">` is already set (layout.tsx:26) and the Inter font already loads the `cyrillic` subset — Cyrillic renders correctly with no further change.

**Verification after applying:** load the app, confirm the nav bar shows the Russian labels and the active-link highlighting still works (the `EXACT`/`startsWith` logic is unchanged).

## One decision for you
Two labels have reasonable alternatives — current picks are in the table above:
- **Dashboard** → "Дашборд" (transliteration, common in RU SaaS) vs. "Панель" / "Сводка".
- **Reading List** → "Список чтения" vs. "Список для чтения".

If you're happy with the table as-is, I'll proceed when you switch out of plan-only mode. As instructed, I've made **no file modifications** and am stopping after the plan.

