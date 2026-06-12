I have a thorough understanding of the architecture. Here's the spec.

# Feature Specification

## Summary

Add **YouTube channels** as a new news source type (`youtube`), alongside the existing `rss`, `telegram`, and `reddit` types. Users will be able to add a YouTube channel as a source; the system will fetch that channel's recent videos and normalize each video into the same article shape used throughout the pipeline (title, link, summary, publishedAt, sourceName), so YouTube content flows through collection, analysis, summarization, and reporting exactly like other sources.

The codebase already has a clean, repeatable pattern for source types: a `SourceType` union, a per-type config object on `RssSource`, a dedicated fetcher/normalizer module, a dispatch branch in `lib/rss/collect.ts`, parallel branches in the create/update/test API routes, and a type-specific UI block in `app/sources/page.tsx`. Adding YouTube means following that pattern, not inventing new infrastructure.

**Key technical opportunity:** YouTube exposes a native, no-auth RSS feed per channel at `https://www.youtube.com/feeds/videos.xml?channel_id=UC…` (returns the ~15 most recent videos). This means YouTube can be ingested **without the YouTube Data API, without an API key, and without quota management** — reusing the existing `fetchFeed()` Atom/RSS parser. This is the lowest-risk approach and should be the default. Use of the official Data API should be treated as out of scope unless richer metadata is required.

## User Stories

- **As a user**, I want to add a YouTube channel as a source by pasting its channel URL or handle, so that new videos from that channel appear in my news collections.
- **As a user**, I want to test a YouTube source before saving it, so that I know it resolves to a valid channel and returns videos.
- **As a user**, I want each video to appear as a news item with its title, a link to the video, a short description, the publish date, and the channel name, so I can analyze and summarize it like any other source.
- **As a user**, I want to limit how many recent videos and over what time window are pulled, consistent with Telegram/Reddit limits, so I control volume.
- **As a user**, I want to edit, deactivate, or delete a YouTube source the same way I manage other sources.
- **As an existing user**, I want my current RSS/Telegram/Reddit sources to keep working unchanged after this feature ships.

## Acceptance Criteria

- [ ] `SourceType` union in `lib/storage/types.ts` includes `"youtube"`.
- [ ] A `YouTubeConfig` interface is added (fields: resolved channel identifier, original input/URL, `maxVideos`/`maxPosts`, `timeWindowDays`, plus the fetch-tracking fields used by other configs) and `RssSource` has an optional `youtube?: YouTubeConfig`.
- [ ] A new fetcher module (e.g. `lib/youtube/fetchYouTubeChannel.ts`) exports a `fetchYouTubeChannel()` returning the standard `{ ok, status, itemCount, error?, articles }` result and a `normalizeYouTube()` that maps a video to `NormalizedArticle`.
- [ ] The fetcher accepts a YouTube channel URL, `@handle`, `channel_id` (`UC…`), or `/channel/UC…`/`/@handle`/`/c/`/`/user/` URL form and resolves it to a usable feed.
- [ ] Each video normalizes to: `title` = video title; `link` = canonical watch URL; `summary` = video description (truncated consistently with other sources) or a sensible fallback; `publishedAt` = video publish date (ISO); `sourceName` = source/channel name.
- [ ] `timeWindowDays` and the max-items limit are applied to YouTube results, matching Telegram/Reddit behavior.
- [ ] Dispatch branch added in `lib/rss/collect.ts` for `type === "youtube" && src.youtube`.
- [ ] Create branch added in `app/api/rss/sources/route.ts` (POST) that validates the YouTube input and persists `sourceType: "youtube"` with a populated `youtube` config.
- [ ] Update branch added in `app/api/rss/sources/[id]/route.ts` (PATCH) for YouTube.
- [ ] Test branch added in `app/api/rss/test/route.ts` for `sourceType === "youtube"`.
- [ ] `app/sources/page.tsx`: YouTube added to the type-selector buttons (with a Russian label, e.g. "YouTube-канал"), a YouTube-specific form block (channel input + maxVideos + timeWindowDays + helper note), the list/display label, `startEdit()` repopulation, and `save()` validation.
- [ ] Invalid input (non-YouTube URL, unresolvable channel) produces a clear, user-visible error in both Test and Save flows; no crash.
- [ ] A channel with zero recent videos returns `status: "empty"` and is handled gracefully (no error state).
- [ ] Existing RSS/Telegram/Reddit sources are unaffected; sources with no `sourceType` still default to `"rss"`.
- [ ] All TypeScript compiles; no type errors introduced.

## Scope

- New `youtube` source type end-to-end: type model, config, fetcher/normalizer, collection dispatch, create/update/test API branches, and the sources-management UI.
- Channel-input resolution supporting channel URL, `@handle`, and `channel_id`.
- Volume controls (max videos, time window) consistent with existing source types.
- Test-before-save support for YouTube.
- Backward compatibility for all existing sources.
- Default ingestion via YouTube's native per-channel RSS/Atom feed (no API key), reusing the existing feed parser where practical.

## Out of Scope

- YouTube Data API v3 integration, OAuth, API keys, and quota management (only if richer metadata than the native feed provides is later required).
- Transcript/caption extraction, video download, or any audio/video processing.
- Playlist, search-query, or "all subscriptions" sources (only single-channel sources).
- LLM summarization of video content beyond the existing pipeline that already runs on `NormalizedArticle` items.
- Thumbnails, view counts, like counts, or other YouTube-specific display enrichments in reports/UI.
- Pagination beyond what the native feed returns (~15 most recent videos).
- Updates to static `src/config/feeds.ts` seed lists (optional, not required).

## Risks

- **Channel-ID resolution:** The native RSS feed requires a `channel_id` (`UC…`). Handles/custom URLs (`/@name`, `/c/name`, `/user/name`) do **not** directly map to a `channel_id` and may require an extra HTML fetch to extract it. This resolution step is the main implementation risk; handle it explicitly and fail clearly when it can't be resolved.
- **Feed format differences:** YouTube feeds are Atom with YouTube/Media RSS namespaces. Confirm the existing `fetchFeed()` parser extracts title, link, publish date, and description correctly; if not, a small dedicated parser may be needed.
- **Description quality:** Some videos have empty/long descriptions; normalization must truncate/fallback consistently with other sources.
- **Anti-bot / rate limiting:** Resolving handles via HTML scraping can be rate-limited or blocked (same class of risk as the Telegram/Reddit scrapers already in the repo). Time-box and degrade gracefully.
- **Live streams / upcoming videos / Shorts:** May have missing or future publish dates; ensure date filtering and sorting don't break.
- **URL ambiguity:** Users may paste a video URL or a feed URL rather than a channel URL; validation should detect and message this.

## Manual Verification Scenarios

1. **Add by channel URL** — Add a source with a standard `https://www.youtube.com/channel/UC…` URL → Test returns recent videos → Save → run a collection → videos appear as news items with correct title, working watch link, date, and channel name.
2. **Add by @handle** — Add a source using `https://www.youtube.com/@SomeChannel` (or `@SomeChannel`) → it resolves to the correct channel and returns videos.
3. **Add by raw channel_id** — Paste `UC…` directly → resolves and fetches.
4. **Invalid input** — Paste a non-YouTube URL and a malformed handle → Test and Save both show a clear error, no crash.
5. **Empty channel** — Use a channel with no videos (or none in the time window) → handled as "empty", no error state, collection still completes.
6. **Volume limits** — Set maxVideos low and timeWindowDays short → result count respects both.
7. **Edit & persist** — Edit an existing YouTube source's limits → reload page → values persisted and re-displayed correctly.
8. **Deactivate/delete** — Toggle active off (excluded from collection) and delete (removed).
9. **Mixed collection** — A collection containing RSS + Telegram + Reddit + YouTube sources collects all four and aggregates them together in analysis/summary/report.
10. **Backward compatibility** — A pre-existing source with no `sourceType` still collects as RSS.

## Decomposition Notes

Split into backlog tasks roughly along the architecture's seams, ordered so each task is independently testable:

1. **Data model & types** — Add `"youtube"` to `SourceType`, define `YouTubeConfig`, add `youtube?` to `RssSource`. Small, foundational; unblocks everything else.
2. **Fetcher + normalizer module** — `lib/youtube/fetchYouTubeChannel.ts` with `normalizeYouTube()`, returning the standard fetch-result shape. Include channel-input → `channel_id` resolution. This is the largest/riskiest task; can be developed and unit-checked in isolation against real channels. Decide here whether to reuse `fetchFeed()` or write a dedicated Atom parser.
3. **Collection dispatch** — Add the `youtube` branch in `lib/rss/collect.ts`. Tiny; depends on (1)+(2).
4. **API: create/update** — YouTube branches in `app/api/rss/sources/route.ts` (POST) and `app/api/rss/sources/[id]/route.ts` (PATCH), including validation and config persistence.
5. **API: test endpoint** — YouTube branch in `app/api/rss/test/route.ts`, reusing the fetcher.
6. **UI** — `app/sources/page.tsx`: type-selector button + Russian label, YouTube form block (channel input, maxVideos, timeWindowDays, helper note), list display label, `startEdit()` repopulation, `save()` validation/parsing.
7. **End-to-end manual QA** — Run the manual verification scenarios above; tighten error messages and edge-case handling.

Tasks 1–3 form the ingestion backbone; 4–6 are the surface area (API + UI); 7 is verification. A reasonable PR grouping is {1+2+3} as the engine, {4+5} as the API, {6} as the UI, with 7 as a final QA pass — though each can also ship independently behind the inactive-until-complete reality that a source type isn't user-reachable until the UI lands.

The single decision worth confirming with stakeholders before task 2: **native RSS feed (no key, simpler, ~15 videos) vs. YouTube Data API (key + quota, richer metadata, more videos).** The spec recommends the native feed; this should be locked before building the fetcher since it determines the module's whole shape.
