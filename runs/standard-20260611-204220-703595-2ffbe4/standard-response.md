# Standard Implementation Response

`tsc` passes. Done.

## Summary

Extended the source data model to recognize Reddit, with no behavior change to existing sources.

**`lib/storage/types.ts`**
- `SourceType` is now `"rss" | "telegram" | "reddit"`.
- Added `RedditConfig` (parallel to `TelegramConfig`): `subredditName`, `webUrl`, `maxPosts`, `timeWindowDays`, plus optional `lastSeenPostId?` / `lastFetchedAt?`.
- Added optional `reddit?: RedditConfig` to `RssSource`.

**`lib/storage/rss.ts`**
- `create` now persists `reddit: input.reddit`. `update` already spreads `patch`, so a `reddit` config round-trips on update with no further change. `sourceType` still defaults to `"rss"` when absent.

**`lib/rss/collect.ts`** (necessary to keep `tsc` green)
- Widened the pre-existing `PerSourceResult.type` from `"rss" | "telegram"` to `SourceType`. No fetcher/route logic added — an unhandled `reddit` source still falls through to the existing default branch, exactly as before.

`tsc --noEmit` passes.
