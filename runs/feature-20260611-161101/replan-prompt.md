# Replan Failed Implementation

The implementation failed validation.

Your job:
1. Analyze the validation failure.
2. Identify the most likely root cause.
3. Produce a minimal fix plan.
4. Apply the fix directly.
5. Do not redesign the feature.
6. Do not touch auth, billing, secrets, database schema, or deployment config.

# Feature Request

Epic task: Task 016 — Finish Sources page remaining English labels

# Approved Plan

# Approved Plan

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



# Implementation Response

# Claude Implementation Response

The two target route files (`app/api/rss/sources/route.ts`, `app/api/rss/sources/[id]/route.ts`) and `app/sources/page.tsx` show no remaining matches — all the other hits are in out-of-scope files we deliberately deferred. Implementation complete.

## Changed files

**`app/sources/page.tsx`** (editor form / modal UI strings):
- Telegram placeholder `or` → `или`
- `Time window` → `Период`; options → `1 день` / `7 дней` / `30 дней`
- Amber note → `Сбор из Telegram читает только недавние публичные посты, а не всю историю канала.`
- `Category` → `Категория`; `Tags (comma-separated)` → `Теги (через запятую)`
- `Active` → `Активен`
- Submit button `Save`/`Add source` → `Сохранить`/`Добавить источник`; `Cancel` → `Отмена`
- ConfirmModal: `Удалить источник?` / `«…» будет удалён.` / `Удалить`

**`app/api/rss/sources/route.ts`** (error strings surfaced as toasts on the page):
- `Invalid JSON.` → `Некорректный JSON.`
- `Name is required.` → `Укажите название.`
- Telegram URL error → `Укажите корректный URL Telegram-канала или @username.`
- `RSS URL is required.` → `Укажите URL RSS-ленты.`
- `URL must start with http:// or https://` → `URL должен начинаться с http:// или https://`

**`app/api/rss/sources/[id]/route.ts`** (same set + `Source not found.` → `Источник не найден.`)

Keys, status codes, and control flow are unchanged everywhere.

## Verification note
- `npx tsc --noEmit` / `npm run typecheck` could **not** run: this worktree has no `node_modules` installed. The edits are pure string-literal swaps inside existing JSX and object literals, so no types changed. I confirmed via grep that no targeted English strings remain in the three files.

## Risks
- **Low.** String-only, trivially reversible. No auth/billing/schema/config touched.
- The Russian error strings now must match the page's toast expectations — they do (page renders `res.json().error` verbatim, so any string displays fine).
- `RSS_CATEGORIES` badge values and example placeholders (`The Hacker News`, `https://example.com/feed`) intentionally left English per the plan.
- The 9 unrelated API routes from the affected-files list were left untranslated per approved scope option (a); if app-wide error translation is wanted, that's a separate task.

Want me to leave the typecheck as-is, or should I `npm install` and run it to be certain?


# Validation Report

# Validation Result

## Overall Result

failed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: failed

Timed Out: False

Exit Code: 1

### STDOUT

```text

[41m                                                                               [0m
[41m[37m                This is not the tsc command you are looking for                [0m
[41m                                                                               [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: failed

Timed Out: False

Exit Code: 127

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build


```

### STDERR

```text
sh: next: command not found

```

