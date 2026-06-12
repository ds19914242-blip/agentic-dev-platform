# Epic

## Summary

Add **YouTube channels** as a first-class news source type (`youtube`) alongside `rss`, `telegram`, and `reddit`. The system ingests a channel's recent videos via YouTube's native no-auth per-channel Atom feed (`https://www.youtube.com/feeds/videos.xml?channel_id=UC…`), normalizes each video into the standard `NormalizedArticle` shape, and flows it through the existing collection → analysis → summarization → reporting pipeline. Implementation follows the established source-type pattern (type union → per-type config → fetcher/normalizer → collection dispatch → API create/update/test branches → sources UI block). No YouTube Data API, no key, no quota.

The work decomposes along architectural seams: an **ingestion backbone** (types → fetcher → dispatch), the **API surface** (create/update + test), the **UI**, and a final **manual QA** pass. The native-RSS-vs-Data-API decision is pre-locked to native RSS per the spec; this is confirmed in Task 001 so the fetcher's shape is settled before it is built.

## Task List

### Task 001 — Lock native-feed decision & extend data model/types

**Goal:** Add the `youtube` source type to the type model and define its config interface, establishing the foundation every other task builds on. Confirm the locked ingestion decision (native RSS feed, no API key) in the task record before building.
**Scope:** Add `"youtube"` to the `SourceType` union. Define a `YouTubeConfig` interface mirroring the existing Telegram/Reddit config shapes: resolved channel identifier (e.g. `channelId`), original user input/URL, a max-items field (`maxVideos`/`maxPosts`), `timeWindowDays`, plus the same fetch-tracking fields the other configs carry. Add optional `youtube?: YouTubeConfig` to `RssSource`. No behavior change yet.
**Suggested files:** `lib/storage/types.ts`
**Acceptance criteria:** `SourceType` includes `"youtube"`; `YouTubeConfig` defined with the fields above; `RssSource` has optional `youtube?`; existing sources with no `sourceType` still default to `"rss"`; TypeScript compiles with no new errors.
**Risk:** low

#### Depends On

_None_

---

### Task 002 — YouTube fetcher + normalizer module

**Goal:** Implement `fetchYouTubeChannel()` and `normalizeYouTube()`, including channel-input → `channel_id` resolution, returning the standard fetch-result shape. This is the largest/riskiest task and is unit-checkable in isolation against real channels.
**Scope:** New module exporting `fetchYouTubeChannel()` returning `{ ok, status, itemCount, error?, articles }` and `normalizeYouTube()` mapping a video to `NormalizedArticle`. Resolve channel input from: raw `channel_id` (`UC…`), `/channel/UC…` URL, `@handle` (bare or URL), `/c/…`, `/user/…` — handles/custom URLs that don't directly carry a `channel_id` require an extra HTML fetch to extract it; time-box and fail clearly when unresolvable. Build the native feed URL and fetch via the existing `fetchFeed()` parser; if Atom/Media-RSS namespace extraction of title/link/date/description is incomplete, add a small dedicated parse step. Normalize each video: `title`=video title, `link`=canonical watch URL, `summary`=description truncated consistently with other sources (sensible fallback when empty), `publishedAt`=ISO publish date, `sourceName`=channel name. Apply `timeWindowDays` and max-items limit matching Telegram/Reddit. Zero recent videos → `status: "empty"` (not an error). Guard against live/upcoming/Shorts items with missing/future dates so filtering and sorting don't break.
**Suggested files:** `lib/youtube/fetchYouTubeChannel.ts` (new); reference `lib/rss/fetchFeed.ts` and the existing Telegram/Reddit fetchers.
**Acceptance criteria:** All resolution forms (channel URL, `@handle`, raw `UC…`, `/channel/`, `/c/`, `/user/`) resolve to a usable feed; normalization fields exactly as specified; `timeWindowDays` + max-items applied; invalid/unresolvable input returns a clear error (no crash); empty channel returns `status: "empty"`; standard result shape returned.
**Risk:** high

#### Depends On

task-001

---

### Task 003 — Collection dispatch branch

**Goal:** Wire YouTube sources into the collection pipeline.
**Scope:** Add a dispatch branch in the collector for `type === "youtube" && src.youtube` that calls `fetchYouTubeChannel()` and feeds results into the same aggregation path as other source types. Tiny glue task.
**Suggested files:** `lib/rss/collect.ts`
**Acceptance criteria:** A source with `sourceType: "youtube"` and a populated `youtube` config is collected via the new fetcher; RSS/Telegram/Reddit branches unchanged; mixed collections aggregate all types together; TypeScript compiles.
**Risk:** low

#### Depends On

task-001, task-002

---

### Task 004 — API create/update branches

**Goal:** Persist YouTube sources via the create and update endpoints with validation.
**Scope:** Add a YouTube branch to the POST route that validates the channel input and persists `sourceType: "youtube"` with a populated `youtube` config. Add the parallel YouTube branch to the PATCH route for editing limits/config. Invalid input (non-YouTube URL, malformed handle) produces a clear, user-visible error with no crash. Follow the existing Telegram/Reddit branches' structure.
**Suggested files:** `app/api/rss/sources/route.ts` (POST), `app/api/rss/sources/[id]/route.ts` (PATCH)
**Acceptance criteria:** POST creates a `youtube` source with validated input and config; PATCH updates a `youtube` source's config; invalid input returns a clear error; existing source types' create/update paths unaffected; TypeScript compiles.
**Risk:** medium

#### Depends On

task-001, task-002

---

### Task 005 — API test-endpoint branch

**Goal:** Support test-before-save for YouTube sources.
**Scope:** Add a branch in the test route for `sourceType === "youtube"` that reuses `fetchYouTubeChannel()` and returns a result indicating whether the input resolves to a valid channel and how many videos it returns. Clear error on invalid/unresolvable input; empty channel reported as empty, not an error.
**Suggested files:** `app/api/rss/test/route.ts`
**Acceptance criteria:** Test branch resolves a valid channel and reports video count; invalid input returns a clear error (no crash); empty channel handled gracefully; other source types' test behavior unchanged.
**Risk:** low

#### Depends On

task-002

---

### Task 006 — Sources management UI block

**Goal:** Expose YouTube end-to-end in the sources page so users can add, test, edit, deactivate, and delete YouTube sources.
**Scope:** In the sources page: add YouTube to the type-selector buttons with a Russian label (e.g. "YouTube-канал"); add a YouTube-specific form block (channel input + `maxVideos` + `timeWindowDays` + helper note about pasting channel URL/handle/ID); add the list/display label; repopulate YouTube fields in `startEdit()`; add YouTube validation/parsing to `save()`. Wire Test and Save to the YouTube API branches. Edited limits must persist and re-display correctly after reload.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** YouTube selectable in the type picker with Russian label; form block renders correct inputs + helper note; list shows a YouTube label; `startEdit()` repopulates; `save()` validates and persists; Test surfaces clear errors for invalid input; edit → reload persists values; deactivate excludes from collection and delete removes; other source types' UI unaffected.
**Risk:** medium

#### Depends On

task-004, task-005

---

### Task 007 — End-to-end manual QA pass

**Goal:** Run the manual verification scenarios end-to-end and tighten error messages/edge-case handling.
**Scope:** Execute all 10 manual verification scenarios (add by channel URL, `@handle`, raw `channel_id`; invalid input; empty channel; volume limits; edit & persist; deactivate/delete; mixed RSS+Telegram+Reddit+YouTube collection; backward compatibility for sources with no `sourceType`). File or fix any gaps in error messaging and edge-case handling (live/upcoming/Shorts dates, empty/long descriptions, video/feed-URL misuse). No new infrastructure.
**Suggested files:** _verification only — touch points across `lib/youtube/fetchYouTubeChannel.ts`, `lib/rss/collect.ts`, the API routes, and `app/sources/page.tsx` as defects surface._
**Acceptance criteria:** All 10 scenarios pass; invalid input shows clear errors in both Test and Save; empty channel handled as `empty`; mixed collections aggregate all four types; pre-`sourceType` sources still collect as RSS; no TypeScript errors.
**Risk:** medium

#### Depends On

task-003, task-006

## Depends On

_None_
