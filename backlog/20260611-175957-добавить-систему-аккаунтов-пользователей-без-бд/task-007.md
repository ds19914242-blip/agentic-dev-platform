PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/36
Type: feature_task
Pipeline: full
Risk: medium
Human Approved: yes
Status: pr_created

### Task 007 — Admin user management API and page

**Goal:** Give admins a UI to list, create, and delete accounts.
**Scope:** Add `GET/POST /api/users` and `DELETE /api/users/[id]`, each gated by `currentUser().role === "admin"` (403 otherwise). Add an `/app/users` page listing accounts with create (incl. role selection) and delete actions; prevent deleting the last admin / self-lockout. Add a NavBar link visible only to admins (optional, can reuse the `/api/auth/me` role).
**Suggested files:** new `app/api/users/route.ts`, new `app/api/users/[id]/route.ts`, new `app/users/page.tsx`, optionally `components/NavBar.tsx`.
**Acceptance criteria:** Admin can list/create/delete users; non-admins get 403 from the APIs and cannot see the page's controls; deleting the last admin is blocked; passwords are hashed on create; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-004


## Human Review

Decision: approved
Reason: Human explicitly approved execution of this auth-related task.
