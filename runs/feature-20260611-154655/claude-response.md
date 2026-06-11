# Claude Response

I have what I need. Here's my analysis and plan.

## Findings

**The real work is one file: `app/collections/page.tsx`.** It's the only affected file with visible UI text. `app/rss/collections/page.tsx` is just a `redirect("/collections")` (no UI). The remaining affected files are API routes.

**Established repo convention** (from the prior "reports" translation, commit `f12d042`): translation tasks changed **only the page component** — `app/reports/page.tsx`, one file, no API routes. The collections page also already partially localizes (`toLocaleDateString("ru-RU")` on line 123), confirming Russian is the target.

**The unrelated API routes should not be touched.** `analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `feedback`, `health/db` are not called by the Collections page, and auth is explicitly off-limits per the rules. The two *collections* API routes (`route.ts`, `[id]/route.ts`) return error strings (`"Name is required."`, `"Collection not found."`, `"Invalid JSON."`) that *can* surface in the page via toast (line 66) — but the prior reports task left such API strings in English, so I'll match that convention and flag it as an optional extension rather than default scope.

## Plan

### Scope
Edit **only** `app/collections/page.tsx`, translating user-visible English strings to Russian. No logic, props structure, class names, API calls, or non-collections files change. Proper nouns (`RSS`, `Telegram`) stay as-is.

### Exact string changes in `app/collections/page.tsx`

| Line | English | Russian |
|---|---|---|
| 53 | `Name is required` | `Введите название` |
| 66 | `Failed` (fallback) | `Ошибка` |
| 67 | `Collection updated` / `Collection created` | `Коллекция обновлена` / `Коллекция создана` |
| 88 | `Collection deleted` | `Коллекция удалена` |
| 99 | `Collections` (h1) | `Коллекции` |
| 100–102 | `Group sources and run analysis directly from a collection.` | `Группируйте источники и запускайте анализ прямо из коллекции.` |
| 105 | `+ New collection` | `+ Новая коллекция` |
| 113 | `No collections yet. Create one to start collecting RSS / Telegram sources.` | `Коллекций пока нет. Создайте коллекцию, чтобы собирать источники RSS / Telegram.` |
| 122 | `{n} sources · updated` | `{n} источников · обновлено` |
| 130 | `Opening…` / `▶ Analyze` | `Открываем…` / `▶ Анализировать` |
| 133 | `Edit` | `Изменить` |
| 138 | `Delete` | `Удалить` |
| 152 | `Edit collection` / `New collection` | `Редактировать коллекцию` / `Новая коллекция` |
| 158 | placeholder `Collection name (e.g. AI Daily)` | `Название коллекции (например, AI Daily)` |
| 164 | placeholder `Description` | `Описание` |
| 170 | `Available (${n})` | `Доступные (${n})` |
| 172 | `All sources added (or none exist yet).` | `Все источники добавлены (или их пока нет).` |
| 179 | `In collection (${n})` | `В коллекции (${n})` |
| 181 | `Click sources on the left to add them.` | `Нажимайте на источники слева, чтобы добавить их.` |
| 192 | `Save collection` / `Create collection` | `Сохранить коллекцию` / `Создать коллекцию` |
| 194 | `Cancel` | `Отмена` |
| 203 | title `Delete collection?` | `Удалить коллекцию?` |
| 204 | `«${name}» will be removed (sources are not deleted).` | `«${name}» будет удалена (источники не удаляются).` |
| 205 | confirmLabel `Delete` | `Удалить` |

Lines 241/244–245 (`Telegram`/`RSS` labels, `+`/`×` icons) stay unchanged.

### Out of scope (intentionally not modified)
- All 12 API routes, including the two collections routes — consistent with the prior reports-page translation. The trade-off: API-originated errors (e.g. duplicate-name failures) would render in English via the line-66 toast. Most user-facing validation already short-circuits client-side (line 53), so this is rare.

### Verification
- `npx tsc --noEmit` / lint to confirm no syntax breakage (only string literals change; template-literal `${...}` interpolations preserved).
- Optionally run the app and visit `/collections` to confirm rendered Russian text.

### Uncertainty to confirm
The affected-files list includes 12 API routes, but convention + the "smallest safe change / don't touch auth" rules point to translating only the page. **Two options:**
1. **(Recommended)** Translate only `app/collections/page.tsx` — matches established convention.
2. Also translate the **two collections API route** error strings so toast errors appear in Russian (auth and other unrelated routes still excluded).

I'd proceed with option 1 unless you want the API error strings localized too. This is plan-only — no files were modified.

