PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/34
Run: standard-20260611-184447-033148-e3b3e4
Type: implementation_task
Pipeline: standard
Risk: high
Status: pr_created

### Task 008 — Scope RSS sources and collections to the active user

**Goal:** Replace the `DEFAULT_OWNER` placeholder so each account only sees and manages its own RSS sources and collections.
**Scope:** In the RSS source/collection route handlers (and `lib/storage/rss.ts` if needed), resolve `currentUser()` and set `ownerId` on create, and filter `list`/`get`/`update`/`delete` by the current user's id. Provide a back-compat path so pre-existing records (owned by `local-user`) remain visible to the admin or are migrated.
**Suggested files:** `app/api/rss/sources/route.ts`, `app/api/rss/sources/[id]/route.ts`, `app/api/rss/collections/route.ts`, `app/api/rss/collections/[id]/route.ts`, `lib/storage/rss.ts`.
**Acceptance criteria:** A user sees only their own sources/collections; cannot read/modify another user's records (404/403); newly created records carry the creator's `ownerId`; legacy `local-user` records are handled per the chosen back-compat rule; `tsc` passes.
**Risk:** high

## Depends On

task-004
