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

### Task 002 — Encode user identity in the session token

**Goal:** Extend the stateless session cookie to carry the authenticated user's id/username/role instead of only `authenticated=true`, keeping signing and verification backward-compatible.
**Scope:** Add `sub` (userId), `username`, and `role` to `SessionPayload`; update `createSessionToken` to accept a user; add a `readSessionPayload(token, secret)` that returns the decoded, verified payload (or `null`). Keep `verifySessionToken` working (boolean) so `middleware.ts` needs no change. Tolerate old-format tokens gracefully (treated as unauthenticated or anonymous).
**Suggested files:** `lib/session.ts`.
**Acceptance criteria:** A token created for a user verifies and decodes back to that user's id/username/role; tampered tokens fail; expired tokens fail; existing boolean `verifySessionToken` behavior preserved; `tsc` passes.
**Risk:** low

## Depends On

_None_

