PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/30
Run: standard-20260611-181924
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 001 — File-based user store with hashed passwords

**Goal:** Introduce a no-DB user store that persists accounts to a JSON file with salted password hashing, plus a one-time bootstrap of the admin account from existing env vars.
**Scope:** Define a `User` type (`id`, `username`, `passwordHash`, `salt`, `role`, `createdAt`) and `UserStorage` interface; implement `LocalUserStorage` (writes `data/users.json`, with `create`, `getByUsername`, `getById`, `list`, `delete`, and a password `verify` helper using `node:crypto` scrypt). Register `userStorage` in the storage index. On first access with an empty store, seed an `admin` user from `APP_USERNAME`/`APP_PASSWORD` if present.
**Suggested files:** `lib/storage/types.ts`, `lib/storage/local.ts`, `lib/storage/index.ts`, new `lib/auth/password.ts` (or inline hashing in the store).
**Acceptance criteria:** `userStorage` is exported and instantiable without opening any DB connection; passwords are stored only as salt+hash; creating then verifying a user round-trips; duplicate usernames are rejected; bootstrap seeds the admin once and is idempotent; `tsc` passes.
**Risk:** medium

## Depends On

_None_
