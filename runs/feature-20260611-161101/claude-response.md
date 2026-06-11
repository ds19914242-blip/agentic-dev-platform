# Claude Response

I've inspected all 12 affected files. Here's what I found and my implementation plan.

## Findings

The project is incrementally translating the UI to Russian (see prior commits and existing Russian toasts/labels). The Sources page still has English UI strings, and the related API routes return English error text that surfaces on that page.

**`app/sources/page.tsx`** — the toasts and list view are already Russian, but the editor form / modal still have English labels:

| Line | Current (English) |
|------|-------------------|
| 287 | placeholder `…/prostoecon or @prostoecon` ("or") |
| 304 | `label="Time window"` |
| 310–312 | `1 day` / `7 days` / `30 days` |
| 317–318 | "Telegram collection reads only recent public posts, not full channel history." |
| 331 | `label="Category"` |
| 344 | `label="Tags (comma-separated)"` |
| 358 | `Active` |
| 362 | `{editingId ? "Save" : "Add source"}` |
| 366 | `Cancel` |
| 375–377 | ConfirmModal `Delete source?` / `«…» will be removed.` / `Delete` |

**`app/api/rss/sources/route.ts`** & **`app/api/rss/sources/[id]/route.ts`** — these return error strings that the Sources page renders directly via `toast((await res.json()).error …)` (page.tsx:97). English strings: `Invalid JSON.`, `Name is required.`, `A valid Telegram channel URL or @username is required.`, `RSS URL is required.`, `URL must start with http:// or https://`, `Source not found.`

**The other 9 affected API routes** (`analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`, `health`, `health/db`) are **not** consumed by the Sources page. They contain a mix of: user-facing error strings shown on *other* pages, and non-UI JSON (the `health` endpoints return ops-only fields like `note: "not using postgres"`).

## Scope decision (the one ambiguity)

The task **title** says "Finish Sources page remaining English labels," but the **affected-files list** includes 9 routes unrelated to the Sources page. These conflict. I'm planning the clearly-correct core and flagging the rest rather than silently expanding scope:

- **In scope (will translate):** `app/sources/page.tsx` UI strings + the two `app/api/rss/sources/**` route error strings (these literally render on the Sources page).
- **Out of the title's scope (recommend deferring):** the 9 other API routes. Their errors appear on other pages, and the `health/*` JSON is ops-only, not a UI label. Translating them here would be scope creep beyond "Sources page," and risks touching `auth` (the rules say don't modify auth unless explicitly required). I recommend leaving them; if the epic wants app-wide error translation, that's a separate task.
- **Intentionally left English:** `RSS_CATEGORIES` values (stored data, shown as badges — translating means a data migration, out of scope) and example placeholders like `The Hacker News` / `https://example.com/feed`.

## Plan

1. **`app/sources/page.tsx`** — replace the English UI strings only (no logic change):
   - `Time window` → `Период`; options → `1 день` / `7 дней` / `30 дней`
   - Amber note → e.g. `Сбор из Telegram читает только недавние публичные посты, а не всю историю канала.`
   - `Category` → `Категория`; `Tags (comma-separated)` → `Теги (через запятую)`
   - `Active` → `Активен`
   - `Save`→`Сохранить`, `Add source`→`Добавить источник`, `Cancel`→`Отмена`
   - ConfirmModal: title `Удалить источник?`, message `«…» будет удалён.`, confirmLabel `Удалить`
   - placeholder "or" → "или"

2. **`app/api/rss/sources/route.ts`** and **`app/api/rss/sources/[id]/route.ts`** — translate the returned `error` string values (POST/PATCH validation + `Source not found.`) to Russian, matching the page's existing toast phrasing (e.g. `Укажите название`, `Укажите URL RSS-ленты`, `URL должен начинаться с http:// или https://`, `Источник не найден`). Keep keys, status codes, and control flow unchanged.

3. **Verify**: typecheck/build (`npm run build` or `tsc`), and manually confirm the Sources editor + delete modal render Russian and that a validation error (e.g. empty name posted directly) returns Russian text.

All changes are string-only and trivially reversible. No auth/billing/schema/config touched.

**Before I treat the 9 extra routes as out-of-scope** — do you want me to (a) keep this plan focused on the Sources page only, or (b) also translate user-facing error strings across the other listed routes? My recommendation is (a). Let me know and I'll finalize.

