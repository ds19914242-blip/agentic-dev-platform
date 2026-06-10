# Architecture Review

## Feature Request

Fully translate the RSS application user interface to Russian

## Planner Input

I now have a complete picture. The affected files are API routes that return English error strings (which surface in the UI as toasts/error states) plus lib/collector files that are mostly internal. Here is the plan.

# Implementation Plan

## Summary

"Fully translate the RSS UI to Russian" for this file set means translating the **user-facing error messages** returned by the RSS-related API routes (they surface in the UI via toasts/error banners) into Russian. The `page.tsx` redirects, the RSS collector, and the feed parser contain **no UI-facing strings** — they hold console logs, exception pass-throughs, and parser-format labels that must stay as-is. The core work is mechanical string replacement across 8 API route files.

## Files To Inspect

- **Translate (user-facing API error strings):**
  - `app/api/rss/collect/route.ts` — `"Invalid JSON."`, `"collectionId is required."`, `"Collection failed."`, `"No articles collected (check that sources are active and reachable)."`
  - `app/api/rss/collections/route.ts` — `"Invalid JSON."`, `"Name is required."`
  - `app/api/rss/collections/[id]/route.ts` — `"Invalid JSON."`, `"Name is required."`, `"Collection not found."`
  - `app/api/rss/sources/route.ts` — `"Invalid JSON."`, `"Name is required."`, `"A valid Telegram channel URL or @username is required."`, `"RSS URL is required."`, `"URL must start with http:// or https://"`
  - `app/api/rss/sources/[id]/route.ts` — `"Invalid JSON."`, `"Source not found."`, `"Name is required."`, Telegram/URL messages (same as above)
  - `app/api/rss/summarize/route.ts` — `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`, `"Summary generation failed."`
  - `app/api/rss/test/route.ts` — `"Invalid JSON."`, Telegram message, `"A valid http(s) URL is required."`
  - `app/api/feedback/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`

- **Do NOT translate (no UI strings / would break behavior):**
  - `app/rss/collections/page.tsx`, `app/rss/page.tsx` — `redirect()` only, zero text
  - `lib/rss/collect.ts` — `serialize()` labels (`Title:`, `Summary:`, `Link:`) are parser contract, must stay English; `"Collection not found."` / `"Collection failed."` already surface via the route (translate the route's fallback)
  - `lib/rss/fetchFeed.ts`, `src/collector/fetchFeeds.ts` — `console.log/warn` and exception `err.message` pass-throughs (library-generated English, not our copy)

## Implementation Steps

1. In each of the 8 API route files, replace the English string literal inside every `NextResponse.json({ error: "..." })` with a Russian equivalent. Keep keys like `collectionId`, `articleId`, `uploadId`, `ANTHROPIC_API_KEY`, `http://`/`https://` verbatim inside the Russian sentence.
2. Use one consistent translation per repeated phrase so the same error reads identically everywhere:
   - `"Invalid JSON."` → `"Некорректный JSON."`
   - `"Name is required."` → `"Укажите название."`
   - `"Collection not found."` → `"Подборка не найдена."`
   - `"Source not found."` → `"Источник не найден."`
   - `"A valid Telegram channel URL or @username is required."` → `"Требуется корректная ссылка на Telegram-канал или @username."`
   - `"URL must start with http:// or https://"` → `"URL должен начинаться с http:// или https://"`
   - …and so on for the remaining strings.
3. Leave HTTP status codes, control flow, and all non-error-message code untouched.
4. Do not modify `collect.ts` `serialize()`, the redirect pages, or the collector/parser logging.

## Validation Steps

1. `npx tsc --noEmit` (or the project's typecheck) — confirm no type/syntax breakage from the edited string literals.
2. Run the dev server and trigger each error path in the UI (submit a source with a blank name, an invalid URL, a non-Telegram URL marked Telegram, summarize without API key) — confirm the toast/error banner shows Russian text.
3. Run an actual collection through `/api/rss/collect` end-to-end to confirm the parser still ingests `serialize()` output (proves the English parser labels were left intact).

## Risks

- **Parser breakage:** Translating the `Title:`/`Summary:`/`Link:` labels in `lib/rss/collect.ts serialize()` would break the deterministic parser. Must leave them English. (Excluded above.)
- **Non-translatable errors:** `fetchFeed`/`fetchFeeds` surface `err.message` from `rss-parser`/network — these stay English regardless; out of scope.
- **Encoding:** Ensure files remain UTF-8 so Cyrillic renders correctly (default here, low risk).
- **Consistency with prior work:** Sources/reports pages were already translated in recent commits — reuse their wording/tone for shared terms (e.g. "источник", "подборка") to avoid mixed terminology.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/rss/collect/route.ts
- API route: app/api/rss/collections/[id]/route.ts
- API route: app/api/rss/collections/route.ts
- API route: app/api/rss/sources/[id]/route.ts
- API route: app/api/rss/sources/route.ts
- Other: src/collector/fetchFeeds.ts
- Other: app/rss/collections/page.tsx
- Library/module: lib/rss/collect.ts
- Library/module: lib/rss/fetchFeed.ts
- API route: app/api/feedback/route.ts
- API route: app/api/rss/summarize/route.ts
- API route: app/api/rss/test/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
