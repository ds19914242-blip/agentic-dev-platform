PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/37
Run: feature-20260611-195909-218992-d8a953
Type: feature_task
Pipeline: full
Risk: medium
Status: pr_created
Human Approved: yes

### Task 011 — Create missing local registration route and page

**Goal:** Add the missing registration flow.

**Problem:** The app currently has login/logout/me endpoints and a login page, but no registration page or registration API route.

**Required files:**
- `app/register/page.tsx`
- `app/api/auth/register/route.ts`

**Acceptance criteria:**
- `app/register/page.tsx` exists.
- `app/api/auth/register/route.ts` exists.
- Login page links to `/register`.
- User can create a local account with email and password.
- Created account can be used to log in.
- No real database is added.
- No external auth provider is added.
- Validation passes.

**Risk:** medium

## Depends On

task-006
