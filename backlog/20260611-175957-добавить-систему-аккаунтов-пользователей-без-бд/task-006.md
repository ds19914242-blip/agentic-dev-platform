PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/35
Run: feature-20260611-185639-771963-988cc3
Type: feature_task
Pipeline: full
Risk: medium
Human Approved: yes
Status: pr_created

### Task 006 — Self-registration API and page

**Goal:** Let new users create a (non-admin) account and land logged in.
**Scope:** Add `POST /api/auth/register` that validates input, rejects duplicate usernames, creates a `user`-role account via `userStorage`, and sets an identity session. Add a `/register` page mirroring the login page's styling with a link between the two. Add `register` to the public paths in the `middleware.ts` matcher so the page and endpoint are reachable while logged out.
**Suggested files:** new `app/api/auth/register/route.ts`, new `app/register/page.tsx`, `middleware.ts`, `app/login/page.tsx` (add link).
**Acceptance criteria:** Registering a fresh username creates the account, logs in, and redirects to `/dashboard`; duplicate username returns a clear error; new accounts get `role: "user"`; `/register` is reachable while unauthenticated; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-002


## Human Review

Decision: approved
Reason: Human explicitly approved execution of this auth-related task.
