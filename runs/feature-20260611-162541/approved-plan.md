# Approved Plan

## Plan: Task 001 — Translate NavBar navigation links

I inspected the repository before planning, and I need to stop and flag a significant mismatch rather than propose changes.

### What I found

**1. The NavBar is already fully translated to Russian.** `components/NavBar.tsx` (the only NavBar in the repo) already has every navigation label and the logout button in Russian:

| Link | Label |
|------|-------|
| `/dashboard` | Панель |
| `/sources` | Источники |
| `/collections` | Коллекции |
| `/` | Запуск анализа |
| `/reports` | Отчёты |
| `/templates` | Шаблоны |
| `/feedback` | Обратная связь |
| `/reading-list` | Список чтения |
| `/settings` | Настройки |
| logout button | Выйти |

The only remaining English string is the brand name `RSS Agent Lab` (a product name, normally not translated). Git history confirms this was done in commit `9fcb163 "Epic task: Task 001 — Translate NavBar navigation links"` and is intact on the current branch (no English nav labels found anywhere, no other NavBar copies in `src/`, `www/`, or `android/`).

**2. The listed "Affected Files" are all backend API routes** (`app/api/analyze`, `app/api/auth/*`, `app/api/benchmark`, `app/api/favorites/*`, etc.). These contain JSON/cookie/handler logic — no navigation links and no NavBar-related UI text. For example, `app/api/auth/logout/route.ts` is purely session-cookie clearing. Translating NavBar links would not touch any of these files, and the task rules explicitly say not to modify auth/API logic unless required.

### Why I'm stopping instead of planning edits

There is a contradiction between the three inputs:
- **Task title** → translate NavBar nav links → **already complete**, nothing to do.
- **Affected files** → API routes → **unrelated** to the task and off-limits per the rules (no touching auth/billing/etc. unless required).

Making edits to the API routes to "satisfy" the affected-files list would be wrong (it would modify auth/handler code for no functional reason and risk breaking endpoints). Re-translating the NavBar is a no-op.

### Recommended action

No code changes. The task appears already delivered. Before anything proceeds, I'd want one of these clarified:

1. **Is this task already considered done?** If so, it can be closed — the NavBar links are translated.
2. **Was the wrong file list attached?** If the real intent is to translate something else (e.g., user-facing strings *returned by* those API routes, or a different component), tell me the actual target and I'll plan that.
3. **Should the brand string `RSS Agent Lab` be localized too?** That's the only untranslated text in the NavBar, but it's a product name — I'd leave it unless you confirm otherwise.

How would you like to proceed?

