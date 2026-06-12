PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/51
Run: standard-20260612-123235-557644-289b86
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 005 — API test-endpoint branch

**Goal:** Support test-before-save for YouTube sources.
**Scope:** Add a branch in the test route for `sourceType === "youtube"` that reuses `fetchYouTubeChannel()` and returns a result indicating whether the input resolves to a valid channel and how many videos it returns. Clear error on invalid/unresolvable input; empty channel reported as empty, not an error.
**Suggested files:** `app/api/rss/test/route.ts`
**Acceptance criteria:** Test branch resolves a valid channel and reports video count; invalid input returns a clear error (no crash); empty channel handled gracefully; other source types' test behavior unchanged.
**Risk:** low

## Depends On

task-002
