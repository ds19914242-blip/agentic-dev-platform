Run: feature-20260611-195206-857720-6a57d9
Type: feature_task
Pipeline: full
Risk: medium
Status: done_no_pr
Human Approved: yes

### Task 010 — Add local registration page and API

**Goal:** Add a local-only registration flow so users can create an account without a database.

**Problem:** The app has login/logout/session endpoints, but there is no visible way to register a new local user.

**Scope:** Local-only auth. No real database. No external auth provider.

**Suggested files:** `app/register/page.tsx`, `app/api/auth/register/route.ts`, `lib/auth/*`, `lib/session.ts`

**Acceptance criteria:**
- A `/register` page exists.
- User can enter email and password.
- Registration stores the user locally using the existing local auth/session architecture.
- After registration, user can log in with the created credentials.
- Login page links to registration page.
- Existing login/logout/profile behavior remains unchanged.
- Validation passes.

**Risk:** medium

## Depends On

task-006
