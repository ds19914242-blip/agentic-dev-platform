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

### Task 005 — API test-endpoint branch

**Goal:** Support test-before-save for YouTube sources.
**Scope:** Add a branch in the test route for `sourceType === "youtube"` that reuses `fetchYouTubeChannel()` and returns a result indicating whether the input resolves to a valid channel and how many videos it returns. Clear error on invalid/unresolvable input; empty channel reported as empty, not an error.
**Suggested files:** `app/api/rss/test/route.ts`
**Acceptance criteria:** Test branch resolves a valid channel and reports video count; invalid input returns a clear error (no crash); empty channel handled gracefully; other source types' test behavior unchanged.
**Risk:** low

## Depends On

task-002

