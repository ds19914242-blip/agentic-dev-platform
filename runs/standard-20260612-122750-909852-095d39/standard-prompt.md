# Standard Task Execution

You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: implementation_task
Pipeline: standard
Risk: medium
Status: in_progress

### Task 002 — YouTube fetcher + normalizer module

**Goal:** Implement `fetchYouTubeChannel()` and `normalizeYouTube()`, including channel-input → `channel_id` resolution, returning the standard fetch-result shape. This is the largest/riskiest task and is unit-checkable in isolation against real channels.
**Scope:** New module exporting `fetchYouTubeChannel()` returning `{ ok, status, itemCount, error?, articles }` and `normalizeYouTube()` mapping a video to `NormalizedArticle`. Resolve channel input from: raw `channel_id` (`UC…`), `/channel/UC…` URL, `@handle` (bare or URL), `/c/…`, `/user/…` — handles/custom URLs that don't directly carry a `channel_id` require an extra HTML fetch to extract it; time-box and fail clearly when unresolvable. Build the native feed URL and fetch via the existing `fetchFeed()` parser; if Atom/Media-RSS namespace extraction of title/link/date/description is incomplete, add a small dedicated parse step. Normalize each video: `title`=video title, `link`=canonical watch URL, `summary`=description truncated consistently with other sources (sensible fallback when empty), `publishedAt`=ISO publish date, `sourceName`=channel name. Apply `timeWindowDays` and max-items limit matching Telegram/Reddit. Zero recent videos → `status: "empty"` (not an error). Guard against live/upcoming/Shorts items with missing/future dates so filtering and sorting don't break.
**Suggested files:** `lib/youtube/fetchYouTubeChannel.ts` (new); reference `lib/rss/fetchFeed.ts` and the existing Telegram/Reddit fetchers.
**Acceptance criteria:** All resolution forms (channel URL, `@handle`, raw `UC…`, `/channel/`, `/c/`, `/user/`) resolve to a usable feed; normalization fields exactly as specified; `timeWindowDays` + max-items applied; invalid/unresolvable input returns a clear error (no crash); empty channel returns `status: "empty"`; standard result shape returned.
**Risk:** high

## Depends On

task-001

