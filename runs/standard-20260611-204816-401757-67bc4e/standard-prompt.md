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

