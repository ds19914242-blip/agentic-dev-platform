# Claude Response

I now have everything I need. The previous translation tasks (Hero, Dashboard) each modified exactly **one** UI file and left all API routes untouched — the API routes listed under "Affected Files" only contain JSON error strings (`"Invalid JSON."`, `"Not found."`) that the Reading List page never renders. I'll keep scope consistent with that pattern.

## Implementation Plan — Task 006: Translate Reading List page

### Scope
**One file changed:** `app/reading-list/page.tsx`

The 11 `app/api/**` routes listed under Affected Files are **out of scope**. They return machine-readable JSON error strings that are not displayed by this page, and no prior translation task (Hero → `components/Hero.tsx`, Dashboard → `app/dashboard/page.tsx`) touched API routes. Translating them would be a larger, riskier change outside "translate the page." I'll leave them unmodified.

### Approach
Replace user-facing English UI strings with Russian, matching the wording and conventions already established in the Dashboard commit (e.g. `(untitled)` → `(без названия)`, and reusing the exact "Nothing saved yet…" translation). No logic, props, state literals (`"all"/"unread"/"read"`), CSS classes, brand labels (`Telegram`), or the existing `ru-RU` date locale change.

### Exact string changes in `app/reading-list/page.tsx`

| Line | English | Russian |
|------|---------|---------|
| 44 | `Reading List` | `Список для чтения` |
| 45 | `Articles you saved for later.` | `Статьи, сохранённые на потом.` |
| 55 | `All` / `Unread` / `Read` (filter chips) | `Все` / `Непрочитанные` / `Прочитанные` |
| 31 | toast `"Removed"` | `"Удалено"` (keep 2nd arg `"success"`) |
| 65 | `Nothing saved yet — use ⭐ Save for Later on report articles.` | `Пока ничего не сохранено — используйте ⭐ «Сохранить на потом» в статьях отчёта.` *(reuse exact Dashboard wording)* |
| 66 | `Nothing for this filter.` | `Для этого фильтра ничего нет.` |
| 81 | `Read` (badge) | `Прочитано` |
| 85 | `(untitled)` | `(без названия)` *(matches Dashboard)* |
| 91 | `saved` (in `{f.source} · saved {date}`) | `сохранено` |
| 102 | `Open Source ↗` | `Открыть источник ↗` |
| 109 | `Mark unread` / `Mark as Read` | `Отметить непрочитанным` / `Отметить прочитанным` |
| 115 | `Remove` | `Удалить` |

**Left unchanged:** line 73 `Telegram` badge (brand name), the `["all","unread","read"]` filter state values, `toLocaleDateString("ru-RU")` (already localized), and all `className`/structure.

### Verification (post-edit, manual)
- `npx tsc --noEmit` (or project's typecheck) to confirm no syntax breakage — only string literals change, so this is low-risk.
- Visually confirm the page renders Russian text and that filter buttons / read-toggle still work (state values untouched).

### Risk & reversibility
Minimal, fully reversible — a single file of string-literal swaps with no behavioral change. One small judgment call: filter-chip and button phrasings (e.g. "Отметить прочитанным") are my proposed wording; if you have preferred terminology, flag it and I'll adjust.

Stopping here per plan-only mode — no files modified.

