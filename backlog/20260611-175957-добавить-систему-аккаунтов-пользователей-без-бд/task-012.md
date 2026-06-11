PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/38
Run: standard-bugfix-20260611-201535-172358-6a39d0
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Status: pr_created
Human Approved: yes

### Task 012 — Fix registration/login persistence mismatch

**Goal:** Make accounts created through `/register` usable immediately on `/login`.

**Problem:** Registration page exists, but after registering a new account, login with the same credentials fails.

**Expected behavior:**
- User registers with email and password.
- User can then log in with the same email and password.
- Session is created successfully.
- Profile/protected page works after login.

**Scope:** Local-only auth. No real database. No external auth provider.

**Acceptance criteria:**
- Registration and login use the same local account storage mechanism.
- A newly registered account can log in successfully.
- Login error still appears for invalid credentials.
- Existing seeded/old users still work.
- Validation passes.
- Add or update a lightweight test/manual verification note covering register → login.

**Risk:** medium

## Depends On

task-011
