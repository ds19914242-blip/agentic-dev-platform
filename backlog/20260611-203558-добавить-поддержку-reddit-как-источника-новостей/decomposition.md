# Epic

## Summary

Add **Reddit** as a first-class news source alongside the existing **RSS** and **Telegram** sources. The codebase already implements a clean discriminated-union pattern on a `sourceType` field (`"rss" | "telegram"`), with Telegram acting as the reference implementation for a non-RSS source: a dedicated fetcher module (`lib/telegram/fetchTelegramChannel.ts`), a nested config object on `RssSource` (`telegram?: TelegramConfig`), and branching in the collector, API routes, test endpoint, and UI.

Reddit support will mirror this pattern: extend the discriminator to `"reddit"`, add a `RedditConfig`, build a lightweight public Reddit fetcher (subreddit JSON, no OAuth), and thread the new kind through collection, the sources API, the test endpoint, and the sources UI. Tasks are decomposed so the type foundation and fetcher land first, then independent wiring tasks (collector, API, test endpoint, UI, article display) can largely proceed in parallel.

## Assumptions

- Reddit will be read via Reddit's **public, unauthenticated JSON endpoints** (e.g. `https://www.reddit.com/r/<subreddit>/new.json` or `/top.json`), matching the lightweight, no-auth approach used for Telegram (`https://t.me/s/<username>`). No OAuth/app credentials are introduced in this epic.
- A descriptive `User-Agent` header will be sent (Reddit blocks default/empty agents); honoring basic rate limits is acceptable for a single-subreddit fetch.
- A "Reddit source" maps to a **single subreddit** (input accepts `r/<sub>`, `<sub>`, or a full `reddit.com/r/<sub>` URL), analogous to one Telegram channel per source.
- Reddit sources reuse the same `maxPosts` / `timeWindowDays` controls as Telegram, with sensible caps/defaults.
- Fetched Reddit posts normalize into the existing `NormalizedArticle` shape (`title`, `link`, `summary`, `publishedAt`, `sourceName`) so the downstream summarization/analysis/serialization pipeline needs no changes.
- No automated test suite exists in the repo; validation is via `tsc` typecheck and manual/`/api/rss/test` smoke checks.
- Existing stored sources without a `sourceType` continue to default to `"rss"` (back-compat preserved).

## Task List

### Task 001 — Add Reddit to source type model and storage types

**Goal:** Extend the source data model so Reddit is a recognized source kind with its own config, without changing existing behavior.
**Scope:** Add `"reddit"` to the `SourceType` union; add a `RedditConfig` interface (parallel to `TelegramConfig`); add an optional `reddit?: RedditConfig` field to `RssSource`. Ensure the local storage layer (create/update) accepts and persists the new field and default. No fetcher or route logic yet.
**Suggested files:** `lib/storage/types.ts`, `lib/storage/rss.ts`
**Acceptance criteria:**
- `SourceType` is `"rss" | "telegram" | "reddit"`.
- `RedditConfig` exists with at least `subredditName: string`, `webUrl: string`, `maxPosts: number`, `timeWindowDays: number` (plus any optional fields like `lastFetchedAt?`).
- `RssSource` gains optional `reddit?: RedditConfig`.
- Storage create/update round-trips a `reddit` config and still defaults missing `sourceType` to `"rss"`.
- `tsc` passes; no existing source behavior changes.
**Risk:** low

#### Depends On
_None_

---

### Task 002 — Build the Reddit fetcher module

**Goal:** Implement a self-contained Reddit subreddit fetcher mirroring `fetchTelegramChannel.ts`, producing normalized articles.
**Scope:** Create a fetcher that takes a subreddit + `maxPosts`/`timeWindowDays`, calls Reddit's public JSON endpoint with a proper `User-Agent`, parses posts, applies the time-window filter, caps post count, and returns the same result shape used by the collector (status, itemCount, error, and `NormalizedArticle[]`). Include a `normalizeReddit(input)` helper that accepts `r/<sub>`, `<sub>`, and full URLs and returns `{ subredditName, webUrl }`. Define default/cap constants (e.g. default max posts, hard cap, default window days).
**Suggested files:** `lib/reddit/fetchRedditSubreddit.ts` (new), referencing `lib/rss/fetchFeed.ts` `NormalizedArticle` for the output shape and `lib/telegram/fetchTelegramChannel.ts` as the structural template.
**Acceptance criteria:**
- `normalizeReddit` correctly parses the documented input forms and rejects invalid input (returns `null` or throws consistently with Telegram's pattern).
- Fetcher returns normalized articles with `title`, `link`, `summary`, `publishedAt`, `sourceName`, and a `sourceType: "reddit"` marker where the Telegram equivalent sets one.
- Network/parse failures return a structured error result instead of throwing uncaught.
- Time-window filtering and max-post cap are applied.
- `tsc` passes; module is importable and has no side effects on import.
**Risk:** medium

#### Depends On
task-001

---

### Task 003 — Wire Reddit into the collection pipeline

**Goal:** Make `collectCollection` fetch Reddit sources and include them in aggregated articles and per-source stats.
**Scope:** Add a `sourceType === "reddit"` branch in the collector dispatch (alongside the existing telegram/rss branches), call the Reddit fetcher, merge its articles into the dedup/serialization flow, and update the source's `lastFetchedAt`/`lastStatus`/`lastError`/`lastItemCount`. Extend `PerSourceResult.type` to include `"reddit"`.
**Suggested files:** `lib/rss/collect.ts`
**Acceptance criteria:**
- Collecting a collection containing a Reddit source produces normalized "Новость #" entries from Reddit posts.
- `PerSourceResult` reports `type: "reddit"` and accurate `itemCount`/`status`/`error` for Reddit sources.
- RSS and Telegram collection behavior is unchanged.
- Dedup logic still applies across mixed-source results.
- `tsc` passes.
**Risk:** medium

#### Depends On
task-001, task-002

---

### Task 004 — Support Reddit in the sources API (create/update)

**Goal:** Allow creating and editing Reddit sources via the sources API with validation.
**Scope:** In the POST (`/api/rss/sources`) and PATCH (`/api/rss/sources/[id]`) handlers, add a `sourceType === "reddit"` branch: validate the subreddit input via `normalizeReddit`, build a `RedditConfig` (subredditName, webUrl, maxPosts, timeWindowDays with caps/defaults), and persist. Support converting a source to/from `"reddit"` the way telegram conversion is handled. Reuse the existing `maxPosts`/`timeWindowDays` body fields.
**Suggested files:** `app/api/rss/sources/route.ts`, `app/api/rss/sources/[id]/route.ts`
**Acceptance criteria:**
- POST with `sourceType: "reddit"` and a valid subreddit creates a source with a populated `reddit` config; invalid subreddit input returns a 400 with a clear message.
- PATCH can edit Reddit source fields and switch a source's type to/from `"reddit"`.
- RSS and Telegram create/update paths are unchanged.
- `tsc` passes.
**Risk:** medium

#### Depends On
task-001, task-002

---

### Task 005 — Support Reddit in the source test endpoint

**Goal:** Let users test-fetch a Reddit source before saving, like RSS/Telegram.
**Scope:** Add a `sourceType === "reddit"` branch to `/api/rss/test` that calls the Reddit fetcher and returns the standard `{ ok, status, itemCount, error?, sample }` response with a few sample titles.
**Suggested files:** `app/api/rss/test/route.ts`
**Acceptance criteria:**
- Testing a valid subreddit returns `ok: true` with `itemCount > 0` and sample titles when posts exist.
- Testing an invalid/empty subreddit returns `ok: false` with an error message.
- RSS/Telegram test behavior is unchanged.
- `tsc` passes.
**Risk:** low

#### Depends On
task-002

---

### Task 006 — Add Reddit to the Sources UI (selector, form, badge)

**Goal:** Surface Reddit in the sources management page so users can add, edit, and identify Reddit sources.
**Scope:** Add a "Reddit" option to the source-type selector; render a Reddit-specific form branch (subreddit input + `maxPosts` + `timeWindowDays`) reusing the Telegram form pattern; wire the test button to the Reddit test path; display a distinct "Reddit" badge and a Reddit-appropriate detail line (e.g. `r/<sub> · N постов / Xд`) in the source list.
**Suggested files:** `app/sources/page.tsx` (and `app/rss/page.tsx` if it duplicates the source form/badge rendering)
**Acceptance criteria:**
- The UI offers RSS / Telegram / Reddit as selectable source types.
- Selecting Reddit shows the subreddit + posts/window controls and submits `sourceType: "reddit"`.
- The source list renders a "Reddit" badge and correct detail line for Reddit sources.
- Existing RSS/Telegram UI is unchanged.
- `tsc` passes; page compiles and renders.
**Risk:** medium

#### Depends On
task-004

---

### Task 007 — Recognize Reddit sources in article display and favorites

**Goal:** Ensure saved/displayed articles correctly attribute Reddit as their source type.
**Scope:** Update the article source-type detection (currently hostname-based: `t.me → telegram`, else `rss`) so Reddit links (`reddit.com` / `redd.it`) are tagged `"reddit"`, and ensure favorites/reading-list store the `"reddit"` `sourceType`. Add any minimal styling/label for a Reddit source where Telegram/RSS are already distinguished.
**Suggested files:** `components/NewsCard.tsx`, `lib/saveFavorite.ts` (and `lib/storage/types.ts` `FavoriteArticle.sourceType` comment if it enumerates kinds)
**Acceptance criteria:**
- Articles with Reddit links are detected and labeled as `"reddit"` rather than falling back to `"rss"`.
- Saving a Reddit article to favorites persists `sourceType: "reddit"`.
- Telegram/RSS detection and display are unchanged.
- `tsc` passes.
**Risk:** low

#### Depends On
task-001

## Depends On

_None_
