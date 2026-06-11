# Approved Plan

## Implementation Plan — Task 007: Translate Collections page

### Findings from inspection

**Established pattern:** Every prior translation task (Tasks 001/003/004/006) modified exactly **one** file — the page or component itself — translating only user-facing English strings to Russian. No API routes, types, or logic were touched. I'll follow that precedent.

**Scope decision on the affected-files list:** The task lists 12 files, but most (auth, benchmark, favorites, feedback, analyze, health/db) are unrelated to Collections and the rules forbid touching auth and prefer the smallest safe change. The only file with user-facing Collections UI is `app/collections/page.tsx`. The others:
- `app/rss/collections/page.tsx` — a 4-line redirect to `/collections`; **no strings, no change**.
- `app/api/rss/collections/route.ts` & `[id]/route.ts` — return English `error` strings (e.g. `"Name is required."`). These *can* surface in a toast, but the page already validates client-side before calling the API, and no prior task translated API messages. **Left out of scope** to match precedent and keep the change minimal/reversible (noted as optional below).

### The one file to change: `app/collections/page.tsx`

Translate these visible strings (logic, props, class names, and `toLocaleDateString("ru-RU")` untouched):

| Line | English | Russian |
|---|---|---|
| 53 | `Name is required` | `Укажите название` |
| 66 | `Failed` | `Не удалось` |
| 67 | `Collection updated` / `Collection created` | `Коллекция обновлена` / `Коллекция создана` |
| 88 | `Collection deleted` | `Коллекция удалена` |
| 99 | `Collections` | `Коллекции` |
| 100–102 | `Group sources and run analysis directly from a collection.` | `Группируйте источники и запускайте анализ прямо из коллекции.` |
| 105 | `+ New collection` | `+ Новая коллекция` |
| 113 | `No collections yet. Create one to start collecting RSS / Telegram sources.` | `Коллекций пока нет. Создайте коллекцию, чтобы собирать источники RSS / Telegram.` |
| 122 | `{n} sources · updated` | `{n} источников · обновлено` |
| 130 | `Opening…` / `▶ Analyze` | `Открываем…` / `▶ Анализировать` |
| 133 | `Edit` | `Изменить` |
| 140 | `Delete` | `Удалить` |
| 152 | `Edit collection` / `New collection` | `Изменить коллекцию` / `Новая коллекция` |
| 158 | placeholder `Collection name (e.g. AI Daily)` | `Название коллекции (например, AI Daily)` |
| 164 | placeholder `Description` | `Описание` |
| 170 | `Available (${n})` | `Доступные (${n})` |
| 172 | `All sources added (or none exist yet).` | `Все источники добавлены (или их пока нет).` |
| 179 | `In collection (${n})` | `В коллекции (${n})` |
| 181 | `Click sources on the left to add them.` | `Нажимайте на источники слева, чтобы добавить их.` |
| 192 | `Save collection` / `Create collection` | `Сохранить коллекцию` / `Создать коллекцию` |
| 195 | `Cancel` | `Отмена` |
| 203 | `Delete collection?` | `Удалить коллекцию?` |
| 204 | `«${name}» will be removed (sources are not deleted).` | `«${name}» будет удалена (источники не удаляются).` |
| 205 | confirmLabel `Delete` | `Удалить` |

**Left as-is:** the `"—"` em-dash placeholder (line 120), `"Telegram"` / `"RSS"` labels (line 241, proper nouns), the `+` / `×` symbols (line 245), and all `className`/state/fetch logic.

### Steps
1. Edit `app/collections/page.tsx` with the ~24 string replacements above.
2. Verify nothing else changed: `git diff --stat` should show only that file.
3. (Optional, type-check) run the project's lint/build if configured — no logic changes expected.
4. Commit: `Epic task: Task 007 — Translate Collections page`.

### Out of scope (flagged, not done)
- API error strings in `app/api/rss/collections/route.ts` and `[id]/route.ts` remain English, consistent with all prior tasks. Translating them is a separate, optional follow-up if the epic later requires server-message localization.
- All other listed API routes (auth, benchmark, favorites, feedback, analyze, health) — untouched.

This is a single-file, string-only, fully reversible change matching the existing 6-commit translation pattern. No modifications made — stopping here per plan-only mode.

