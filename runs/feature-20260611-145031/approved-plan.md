# Approved Plan

I've inspected all the affected files. Here's my analysis and plan.

## Findings

The task title is **"Translate Dashboard page."** Following the pattern of prior commits (Task 001 NavBar, Task 003 Hero), these tasks translate visible English UI text to Russian.

Reviewing the affected files, they fall into three groups by how much user-facing English they actually contain:

| File | User-facing English text? | Relevance to "Dashboard page" |
|------|---------------------------|-------------------------------|
| `app/dashboard/page.tsx` | **Yes — extensive** | **This is the `/dashboard` page** (primary target) |
| `components/Dashboard.tsx` | Some leftover labels (mostly already Russian) | The *report* render component (different "dashboard") |
| `components/StatsPanel.tsx` | 2 section labels in English | Used inside the report component |
| `app/api/overview/route.ts` | None — returns only data | Feeds the dashboard, no strings |
| `lib/dashboard.ts` | None — type definitions only | No strings |
| `app/api/analyze`, `benchmark`, `feedback`, `favorites`, `favorites/[id]` | English `{error}` JSON strings | Only surface on failure |
| `app/api/auth/login`, `auth/logout` | English `{error}` strings (login already partly Russian) | **Auth — rules say don't touch unless required** |

Key point: only **`app/dashboard/page.tsx`** is unambiguously "the Dashboard page" with visible UI text. `lib/dashboard.ts` and `app/api/overview/route.ts` contain **no translatable strings at all**. The API routes contain only error messages that surface conditionally, and two of them are auth routes the rules tell me to leave alone.

---

## Plan

### Scope (recommended — smallest safe)

**Translate `app/dashboard/page.tsx` only.** This is the page rendered at `/dashboard` and the only file with substantial visible English UI text directly matching the task title.

#### Strings to translate in `app/dashboard/page.tsx`

| Line(s) | English | Proposed Russian |
|---------|---------|------------------|
| 26 | `Workspace` (eyebrow) | `Рабочее пространство` |
| 27–29 | `Your intelligence dashboard` (keep gradient `<span>` on last word) | `Ваша панель аналитики` (gradient on `аналитики`) |
| 38 | `Run Analysis` | `Запустить анализ` |
| 43 | `Add Source` | `Добавить источник` |
| 50 | `Create Collection` | `Создать коллекцию` |
| 56 | `Overview` | `Обзор` |
| 58–61 | `Sources` / `Collections` / `Reports` / `Favorites` (OverviewCard `label` props) | `Источники` / `Коллекции` / `Отчёты` / `Избранное` |
| 68 | `Latest Reports` | `Последние отчёты` |
| 70 | `View all →` | `Смотреть все →` |
| 76–77 | `No reports yet.` / `Run your first analysis →` | `Отчётов пока нет.` / `Запустите первый анализ →` |
| 87 | `… selected · … trends` | `… выбрано · … трендов` |
| 91 | `Open` | `Открыть` |
| 93 | `Export` | `Экспорт` |
| 105 | `Recent Saved` | `Недавно сохранённое` |
| 110 | `Nothing saved yet — use ⭐ Save for Later on report articles.` | `Пока ничего не сохранено — используйте ⭐ «Сохранить на потом» в статьях отчёта.` |
| 117 | `(untitled)` | `(без названия)` |
| 127 | `Recent Activity` | `Недавняя активность` |
| 131 | `No analysis runs yet.` | `Запусков анализа пока нет.` |

Notes:
- No structural/JSX changes — only the text between tags and the `label="…"` prop strings on lines 58–61. The `OverviewCard` component itself needs no change.
- Dates already use `toLocaleString("ru-RU")` / `toLocaleDateString("ru-RU")` — leave as-is.
- The `▶ ＋ ▣ ⭐` glyphs and all `className`/`href`/routing stay untouched.

### Verification
- `npx tsc --noEmit` (or the project's typecheck) — should pass; changes are string-only.
- Optionally run the app and load `/dashboard` to eyeball the rendered Russian.

### Reversibility
Single-file, text-only diff. Trivially revertible.

---

## Uncertainty to confirm before I implement

The affected-files list is broader than the visible page, so I want your call on scope rather than guess:

1. **`components/Dashboard.tsx` + `StatsPanel.tsx`** — these render the *report* view (a different "dashboard"), already ~80% Russian, with leftover English labels (`Intelligence Report`, `Collected/Selected/Generated`, the four chart titles, `Processing`/`Performance`). Include them, or leave for a separate report-translation task?
2. **API route error strings** (`analyze`, `benchmark`, `feedback`, `favorites`) — these are JSON error messages that only appear on failure. Translate them too?
3. **Auth routes** (`auth/login`, `auth/logout`) — the rules say *don't modify auth unless explicitly required*. They contain English error strings (`Server auth is not configured.`, `Invalid request.`). My default is **to leave these untouched**. Confirm if you want them translated despite the rule.

My recommendation is the minimal scope (page only). Let me know if you want the extended scope and I'll fold the additional strings into the plan.

