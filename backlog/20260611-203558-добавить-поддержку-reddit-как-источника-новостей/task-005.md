PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/41
Run: standard-20260611-204815-190480-eba67f
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

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

## Depends On

_None_
