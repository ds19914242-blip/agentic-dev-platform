# Standard Task Execution

You are fixing a known bug.

Steps:
1. Identify the likely root cause.
2. Make the smallest safe fix.
3. Do not redesign unrelated code.
4. Preserve existing behavior except for the bug.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Status: in_progress
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

