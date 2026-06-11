Run: feature-20260611-192250-454363-215793
Type: feature_task
Pipeline: full
Risk: high
Human Approved: yes
Status: done_no_pr

### Task 009 — Scope favorites and feedback to the active user

**Goal:** Make the reading list (favorites) and relevance feedback per-account rather than global.
**Scope:** Add an owner field to `FavoriteArticle` / `Feedback` (and their storage interfaces), set it from `currentUser()` on create, and filter `list`/`update`/`delete` by the current user in the favorites/feedback route handlers. Keep legacy unowned records handled gracefully (e.g. visible to admin or migrated).
**Suggested files:** `lib/storage/types.ts`, `lib/storage/local.ts`, `app/api/favorites/route.ts`, `app/api/favorites/[id]/route.ts`, `app/api/feedback/route.ts`.
**Acceptance criteria:** Each user sees only their own favorites and feedback; cross-user access is denied; new records carry the owner; legacy records handled per the chosen rule; `tsc` passes.
**Risk:** high

## Depends On

task-004


## Human Review

Decision: approved
Reason: Human explicitly approved execution of this auth-related task.
