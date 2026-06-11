PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/32
Run: standard-20260611-183250
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 004 — Current-user resolution helper and `/api/auth/me`

**Goal:** Provide a server helper to resolve the logged-in user from the request and an endpoint clients can call to learn who they are.
**Scope:** Add a `currentUser(cookies/secret)` helper that reads the session cookie, decodes the payload (Task 002), and loads the user from `userStorage` (Task 001). Add `GET /api/auth/me` returning `{ username, role }` (or 401). Add `api/auth/me` to public-or-authed handling as appropriate (it lives under the already-public `api/auth` matcher prefix, so confirm it 401s cleanly when unauthenticated).
**Suggested files:** new `lib/auth/currentUser.ts`, new `app/api/auth/me/route.ts`.
**Acceptance criteria:** Authenticated request to `/api/auth/me` returns the user's username/role; unauthenticated request returns 401; helper is reusable by other route handlers; `tsc` passes.
**Risk:** low

## Depends On

task-001, task-002
