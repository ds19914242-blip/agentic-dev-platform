Run: standard-20260611-204816-401757-67bc4e
Type: implementation_task
Pipeline: standard
Risk: medium
Status: done_no_pr

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

## Depends On

_None_
