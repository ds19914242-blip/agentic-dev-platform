PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/31
Run: standard-20260611-182228
Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 002 — Encode user identity in the session token

**Goal:** Extend the stateless session cookie to carry the authenticated user's id/username/role instead of only `authenticated=true`, keeping signing and verification backward-compatible.
**Scope:** Add `sub` (userId), `username`, and `role` to `SessionPayload`; update `createSessionToken` to accept a user; add a `readSessionPayload(token, secret)` that returns the decoded, verified payload (or `null`). Keep `verifySessionToken` working (boolean) so `middleware.ts` needs no change. Tolerate old-format tokens gracefully (treated as unauthenticated or anonymous).
**Suggested files:** `lib/session.ts`.
**Acceptance criteria:** A token created for a user verifies and decodes back to that user's id/username/role; tampered tokens fail; expired tokens fail; existing boolean `verifySessionToken` behavior preserved; `tsc` passes.
**Risk:** low

## Depends On

_None_
