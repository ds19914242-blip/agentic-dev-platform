# Approved Plan

I've inspected all affected files plus the actual UI pages. I have a complete picture and one important scope discrepancy to surface. Here is the plan.

---

# Implementation Plan: Translate RSS UI to Russian

## Key finding about the affected-files list

The provided list is **misaligned with where the visible UI text actually lives**:

- `app/rss/page.tsx` and `app/rss/collections/page.tsx` are **3-line redirects** (`redirect("/sources")` / `redirect("/collections")`) — they contain **zero** user-facing text.
- The real buttons, labels, empty states, and toasts live in **`app/sources/page.tsx`** and **`app/collections/page.tsx`**, which are **not** in the affected-files list.
- `src/collector/fetchFeeds.ts` (console logs) and `src/config/feeds.ts` (source-name data) contain **no UI strings** — only server logs and config data.
- `lib/rss/fetchFeed.ts` surfaces only runtime `err.message` — no static UI strings.

So to satisfy the actual request ("translate visible UI text"), the plan **adds the two real page files** and **drops the three no-op files**. I'll flag this rather than silently follow an incomplete list.

## What I will NOT translate (business logic — out of scope by your rules)

| Item | File | Reason |
|---|---|---|
| `serialize()` labels `Title:` / `Summary:` / `Link:` | `lib/rss/collect.ts` | Feed into the deterministic parser — changing them breaks parsing. (`Новость #` / `Дата (UTC)` are already RU.) |
| `RSS_CATEGORIES` values (`AI`, `CyberSec`, `IAM`, `SecOps`, `Vendor`, `Compliance`, `Other`) | `lib/storage/types.ts` | Stored enum values / persisted data. Mostly acronyms; translating changes schema-level data. |
| Status values `ok` / `empty` / `error` (shown raw as `last: ok`) | pages + routes | Enum values used in conditionals and persisted. Translating needs a display map = larger change. |
| `console.log`/`console.warn` strings | `src/collector/fetchFeeds.ts` | Server logs, not UI. |
| Source names (`Market Radar`, etc.) | `src/config/feeds.ts` | Config data, not UI labels. |

## Files to change

### 1. `app/sources/page.tsx` (primary UI)
Translate all literal strings: page header `Sources` → `Источники` + subtitle; `+ New source`; empty state; per-card buttons (`Test`/`Testing…`, `Activate`/`Deactivate`, `Edit`, `Delete`, `last:`); editor heading + all `Field` labels (`Source type`, `Name`, `Max posts`, `Time window`, `Category`, `Tags (comma-separated)`, `Active`, `RSS Feed`/`Telegram Channel`, `1 day`/`7 days`/`30 days`); the Telegram amber note; `Save`/`Add source`/`Cancel`; all `toast(...)` strings (validation + success + test results, incl. units `posts`/`items` → `постов`/`элементов`); `ConfirmModal` title/message/confirmLabel. Keep `RSS`/`Telegram` badges and placeholders' example URLs as-is (proper-noun examples).

### 2. `app/collections/page.tsx` (primary UI)
Translate: header `Collections` + subtitle; `+ New collection`; empty state; card meta (`N sources · updated`); `Analyze`/`Opening…`; `Edit`/`Delete`; editor heading + placeholders; `Pane` titles `Available (n)`/`In collection (n)`; `Empty` helper texts; `Save/Create collection`/`Cancel`; all `toast(...)` strings; `ConfirmModal` title/message/confirmLabel.

### 3. API route `error` JSON strings (surfaced in UI via `toast((await res.json()).error)`)
Translate the user-facing `error` literals in:
- `app/api/rss/collect/route.ts` — `Invalid JSON.`, `collectionId is required.`, `Collection failed.`, `No articles collected (...)`.
- `app/api/rss/collections/route.ts` — `Invalid JSON.`, `Name is required.`
- `app/api/rss/collections/[id]/route.ts` — `Invalid JSON.`, `Name is required.`, `Collection not found.`
- `app/api/rss/sources/route.ts` — `Invalid JSON.`, `Name is required.`, Telegram-URL msg, `RSS URL is required.`, http(s) msg.
- `app/api/rss/sources/[id]/route.ts` — `Invalid JSON.`, `Source not found.`, `Name is required.`, Telegram-URL msg, http(s) msg.
- `app/api/rss/test/route.ts` — `Invalid JSON.`, Telegram-URL msg, `A valid http(s) URL is required.`
- `app/api/rss/summarize/route.ts` — `ANTHROPIC_API_KEY is not set on the server.`, `Expected JSON body.`, `Missing uploadId.`, `Upload not found. Please upload the file again.`, `Summary generation failed.`

### 4. `lib/rss/collect.ts` (one string only)
`"Collection not found."` (line 78) → Russian. This propagates to the UI via `/api/rss/collect`. Leave the `serialize()` labels untouched.

### 5. `components/NavBar.tsx` (recommended, for consistency)
Nav labels `Sources` → `Источники` and `Collections` → `Коллекции` (the logout button is already `Выйти`). Leaving them English would make the nav inconsistent with the now-Russian pages. **Scope note:** NavBar also lists non-RSS pages (Dashboard, Reports, etc.); I'll translate **only** the two RSS-related labels to stay within scope.

## Approach & safety
- Pure string-literal replacements only. No changes to control flow, conditionals, enum comparisons, API contracts, payload keys, schema, or prompts.
- Status/category comparisons (e.g. `r.status === "ok"`, `RSS_CATEGORIES.includes(...)`) are untouched, so logic and persistence are unaffected.
- Fully reversible (text-only diff).
- Verification: `npm run build` / typecheck (no type changes expected), then visual check of `/sources` and `/collections` for layout overflow from longer Russian strings.

## Decisions you may want to override
1. **NavBar labels** (item 5) — include the two RSS nav labels, or leave NavBar entirely alone?
2. **Status/category display** — I'm leaving `ok/error/empty` and category acronyms in English to avoid touching persisted enums. If you want them shown in Russian, that's a separate display-mapping change.

I'll stop here per plan-only mode and won't modify any files. Want me to proceed with these defaults, or adjust the two decisions above first?

