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

### Task 003 — Authenticate login against the user store

**Goal:** Replace the single env-var credential check with lookup + password verification against the user store, issuing an identity-bearing session.
**Scope:** Update `POST /api/auth/login` to fetch the user by username from `userStorage`, verify the password hash in constant time, and on success call the new `createSessionToken(user, secret)`. Preserve the existing cookie attributes, error messages, and 500-when-unconfigured behavior (now keyed on `SESSION_SECRET`).
**Suggested files:** `app/api/auth/login/route.ts`.
**Acceptance criteria:** Valid stored credentials log in and set an identity session cookie; invalid credentials return 401 with the existing Russian error; the seeded admin (from Task 001) can still log in with the env credentials; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-002

