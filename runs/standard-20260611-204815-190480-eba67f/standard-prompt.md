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
Risk: low
Status: in_progress

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

