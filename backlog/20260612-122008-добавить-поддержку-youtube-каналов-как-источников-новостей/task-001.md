PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/49
Run: standard-20260612-122544-870739-084580
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 001 — Lock native-feed decision & extend data model/types

**Goal:** Add the `youtube` source type to the type model and define its config interface, establishing the foundation every other task builds on. Confirm the locked ingestion decision (native RSS feed, no API key) in the task record before building.
**Scope:** Add `"youtube"` to the `SourceType` union. Define a `YouTubeConfig` interface mirroring the existing Telegram/Reddit config shapes: resolved channel identifier (e.g. `channelId`), original user input/URL, a max-items field (`maxVideos`/`maxPosts`), `timeWindowDays`, plus the same fetch-tracking fields the other configs carry. Add optional `youtube?: YouTubeConfig` to `RssSource`. No behavior change yet.
**Suggested files:** `lib/storage/types.ts`
**Acceptance criteria:** `SourceType` includes `"youtube"`; `YouTubeConfig` defined with the fields above; `RssSource` has optional `youtube?`; existing sources with no `sourceType` still default to `"rss"`; TypeScript compiles with no new errors.
**Risk:** low

## Depends On

_None_
