PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/53
Run: standard-20260612-123235-764801-1028d0
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 004 — API create/update branches

**Goal:** Persist YouTube sources via the create and update endpoints with validation.
**Scope:** Add a YouTube branch to the POST route that validates the channel input and persists `sourceType: "youtube"` with a populated `youtube` config. Add the parallel YouTube branch to the PATCH route for editing limits/config. Invalid input (non-YouTube URL, malformed handle) produces a clear, user-visible error with no crash. Follow the existing Telegram/Reddit branches' structure.
**Suggested files:** `app/api/rss/sources/route.ts` (POST), `app/api/rss/sources/[id]/route.ts` (PATCH)
**Acceptance criteria:** POST creates a `youtube` source with validated input and config; PATCH updates a `youtube` source's config; invalid input returns a clear error; existing source types' create/update paths unaffected; TypeScript compiles.
**Risk:** medium

## Depends On

task-001, task-002
