# Claude Response

Confirmed: the API-file matches are unrelated (type imports, enum values like `FeedbackVote`). The NavBar labels live **only** in `components/NavBar.tsx`.

## Implementation Plan — Task 001: Translate NavBar navigation links

### Key finding / uncertainty (please note)
The task's **"Affected Files" list is entirely API routes** (`app/api/**/route.ts`). None of them contain NavBar navigation text — they are backend handlers. The navigation links actually live in a single file: **`components/NavBar.tsx`** (lines 6–16, the `LINKS` array). I verified the API routes contain no navbar labels (the only grep hits were unrelated type/enum identifiers).

I'm proceeding on the assumption that the **intent** is "translate the NavBar nav links to Russian," and the correct target is `components/NavBar.tsx`. The listed API files should **not** be touched. If the intent was actually something API-related, please clarify.

### Current state
- `components/NavBar.tsx` `LINKS` array has 9 English labels (`href` values stay the same — they are routes, not UI text).
- The logout button is already Russian (`"Выйти"`, line 66), so the project is mid-translation and Russian UI is the established direction (matches already-translated `reports`/`feedback` pages, e.g. `"Отчёт удалён"`).

### Proposed change (single file)
Translate only the `label` strings in the `LINKS` array (lines 7–15). Leave all `href`, the `EXACT` set, the brand text "RSS Agent Lab", and logic untouched.

| Line | English label | Russian label |
|------|---------------|---------------|
| 7 | Dashboard | Панель |
| 8 | Sources | Источники |
| 9 | Collections | Коллекции |
| 10 | Run Analysis | Запуск анализа |
| 11 | Reports | Отчёты |
| 12 | Templates | Шаблоны |
| 13 | Feedback | Обратная связь |
| 14 | Reading List | Список чтения |
| 15 | Settings | Настройки |

### Why this is the smallest safe change
- One file, 9 string literals; no logic, routes, or component structure changes.
- No auth/billing/secrets/schema/deploy impact.
- Fully reversible (revert the 9 strings).

### Verification steps (after implementation)
1. `npm run build` (or `next build`) / typecheck — confirm no errors.
2. Run the app and confirm the nav bar renders the Russian labels and active-link highlighting still works (the `EXACT` set and `pathname.startsWith` logic key off `href`, which is unchanged).

### Open question for confirmation
1. The "Affected Files" list contradicts the actual location — confirm I should edit `components/NavBar.tsx` and ignore the API routes.
2. Confirm the proposed Russian wording (especially "Запуск анализа" for *Run Analysis* and "Панель" for *Dashboard*) matches your preferred terminology.

I've stopped here per plan-only mode and made no file changes.

