PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/33
Run: standard-20260611-183609
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 005 — Surface the active account in the NavBar

**Goal:** Show the logged-in username in the header next to the existing logout button.
**Scope:** Fetch `/api/auth/me` from the client `NavBar` and render the username (with a graceful fallback while loading / if it fails). No change to logout behavior.
**Suggested files:** `components/NavBar.tsx`.
**Acceptance criteria:** When logged in, the NavBar displays the current username; logout still works and redirects to `/login`; no hydration warnings; `tsc` passes.
**Risk:** low

## Depends On

task-004
