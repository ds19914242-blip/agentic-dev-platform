Type: feature_task
Pipeline: full
Risk: medium
Human Approved: yes
Status: done_no_pr

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

## Depends On

_None_
