PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/39
Run: standard-20260611-204220-703595-2ffbe4
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

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

## Depends On

_None_
