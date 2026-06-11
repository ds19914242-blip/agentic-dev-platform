# Claude Response

I have everything I need. No files will be modified — here is the plan.

## Implementation Plan — Task 016: Finish Sources page remaining English labels

### Findings

The Sources page (`app/sources/page.tsx`) is already ~80% translated to Russian. The remaining English appears in the editor panel, the delete-confirm modal, and the error messages returned by the two `rss/sources` API routes (which surface verbatim as toasts on this page via `toast((await res.json()).error ?? "Ошибка", "error")`). The shared `ConfirmModal` is already Russian by default, so the only issue there is that `app/sources/page.tsx` passes English props that override it.

### Scope decision (recommended)

The task title scopes this to the **Sources page**. I recommend translating only the strings that are actually visible on that page:

1. `app/sources/page.tsx` — remaining English UI labels
2. `app/api/rss/sources/route.ts` — error strings (shown as toasts on the Sources page)
3. `app/api/rss/sources/[id]/route.ts` — error strings (shown as toasts on the Sources page)

The other 9 affected files (`analyze`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`, `health`, `health/db`, `auth/login`, `auth/logout`) belong to **other pages**, not the Sources page. Their error strings never render on `/sources`. Per the rules ("smallest safe implementation"; "do not modify auth … unless explicitly required"), I propose leaving them out of this task. ⚠️ **This is the one open question** — see bottom.

---

### Change 1 — `app/sources/page.tsx`

| Line | Current (English) | Proposed (Russian) |
|---|---|---|
| 304 | `label="Time window"` | `label="Временное окно"` |
| 310 | `<option value={1}>1 day</option>` | `1 день` |
| 311 | `<option value={7}>7 days</option>` | `7 дней` |
| 312 | `<option value={30}>30 days</option>` | `30 дней` |
| 317–318 | `Telegram collection reads only recent public posts, not full channel history.` | `Сбор из Telegram читает только недавние публичные посты, а не всю историю канала.` |
| 331 | `label="Category"` | `label="Категория"` |
| 344 | `label="Tags (comma-separated)"` | `label="Теги (через запятую)"` |
| 358 | `Active` (checkbox label) | `Активен` |
| 362 | `{editingId ? "Save" : "Add source"}` | `{editingId ? "Сохранить" : "Добавить источник"}` |
| 366 | `Cancel` | `Отмена` |
| 375 | `title="Delete source?"` | `title="Удалить источник?"` |
| 376 | `` message={`«${...}» will be removed.`} `` | `` message={`«${...}» будет удалён.`} `` |
| 377 | `confirmLabel="Delete"` | `confirmLabel="Удалить"` (or remove the prop — `ConfirmModal` already defaults to `"Удалить"`) |

**Leave unchanged** (illustrative placeholders / values, not UI copy): example names `"Prosto Econ"` / `"The Hacker News"` (277), URL placeholders (287, 327), `"news, daily"` (349), the `Telegram`/`RSS` badge text, and category values (rendered from data).
- Minor optional: line 287 placeholder `"https://t.me/prostoecon or @prostoecon"` contains the English word "or" → could become `"… или @prostoecon"`. Low priority; flagging rather than assuming.

### Change 2 — `app/api/rss/sources/route.ts` (error strings → Russian)

| Line | Current | Proposed |
|---|---|---|
| 51 | `"Invalid JSON."` | `"Некорректный JSON."` |
| 54 | `"Name is required."` | `"Укажите название."` |
| 65 | `"A valid Telegram channel URL or @username is required."` | `"Укажите корректный URL Telegram-канала или @username."` |
| 88 | `"RSS URL is required."` | `"Укажите URL RSS-ленты."` |
| 91 | `"URL must start with http:// or https://"` | `"URL должен начинаться с http:// или https://"` |

### Change 3 — `app/api/rss/sources/[id]/route.ts` (error strings → Russian)

| Line | Current | Proposed |
|---|---|---|
| 23 | `"Invalid JSON."` | `"Некорректный JSON."` |
| 27 | `"Source not found."` | `"Источник не найден."` |
| 31 | `"Name is required."` | `"Укажите название."` |
| 48 | `"A valid Telegram channel URL or @username is required."` | `"Укажите корректный URL Telegram-канала или @username."` |
| 70 | `"URL must start with http:// or https://"` | `"URL должен начинаться с http:// или https://"` |

These mirror the wording already used in the client-side validation toasts in `page.tsx` (e.g. lines 60–73), keeping messaging consistent.

---

### Verification (after edits, in execution phase)
- `npx tsc --noEmit` (or the project's typecheck/lint) — these are pure string-literal swaps, so no type impact expected.
- Manually confirm `/sources`: editor labels, the Telegram note, the Active checkbox, Save/Add/Cancel buttons, and the delete modal all render in Russian; trigger a validation error to confirm the toast text is Russian.

### Risk
Very low. All changes are display-string literals; no logic, control flow, types, auth, schema, or config touched. Fully reversible.

---

### ⚠️ Open question for you
The affected-files list includes 9 routes outside the Sources page (`analyze`, `benchmark`, `favorites`, `feedback`, `health*`, `auth/*`). My recommended plan **excludes** them because their strings don't appear on `/sources`, and the rules tell me to keep changes minimal and avoid auth. Do you want me to:
- **(A, recommended)** Translate only the Sources page + its two `rss/sources` routes, or
- **(B)** Also translate the remaining user-facing error strings in the non-auth routes (`analyze`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`) as a broader sweep, still leaving `auth/*` and the machine-only `health*` endpoints untouched?

I'll wait for your direction (or approval of A) before any execution, since this is plan-only.

