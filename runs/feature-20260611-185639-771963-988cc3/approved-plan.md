# Approved Plan

You declined the question, so I'll produce the plan using the **recommended smallest-safe interpretation** and clearly flag the decision points so you can redirect. Since this is `plan_only`, no files are modified.

---

# Implementation Plan — Task 006: Self-registration API and page

## Context & key constraint

The existing auth is **single-admin, identity-less**:
- `app/api/auth/login/route.ts` compares against `APP_USERNAME`/`APP_PASSWORD` env vars.
- `lib/session.ts` issues a cookie encoding only `{ authenticated: true, exp }` — **no user identity**.
- `lib/auth/currentUser.ts` always returns the env admin with `role: "admin"`.
- No `users` table (`scripts/dbInit.ts`), no password-hash dependency (`package.json`).

A real self-registration feature **requires** persisting users with passwords, which the rules permit because it is "explicitly required" by the task. I scope the change as narrowly as possible and follow the codebase's existing patterns.

**Recommended approach (assumed below):** *Full multi-user store*, password hashing via **`node:crypto` scrypt** (no new dependency), session extended to carry the username. Backward compatible: the env admin keeps working.

---

## Files to add

1. **`lib/storage/types.ts`** (edit) — add a `UserRecord` type (`id`, `username`, `passwordHash`, `role`, `createdAt`) and a `UserStorage` interface (`getByUsername`, `create`, `count`).
2. **`lib/storage/local.ts`** (edit) — `LocalUserStorage` persisting to `data/users.json`, mirroring `LocalFavoriteStorage`.
3. **`lib/storage/postgres.ts`** (edit) — `PostgresUserStorage` against a new `users` table.
4. **`lib/storage/index.ts`** (edit) — register `userStorage` (postgres-when-selected, else local), matching the existing pattern at lines 53–73.
5. **`scripts/dbInit.ts`** (edit) — add `CREATE TABLE IF NOT EXISTS users (...)` + unique index on `username` to the idempotent DDL.
6. **`lib/auth/password.ts`** (new) — `hashPassword`/`verifyPassword` using `node:crypto` `scrypt` with a per-user random salt, stored as `scrypt$salt$hash`; timing-safe compare.
7. **`app/api/auth/register/route.ts`** (new) — `POST` handler (mirrors `login/route.ts`): validate body, enforce username/password rules, reject duplicates (409), create user, then issue the session cookie and return `{ ok: true }`.
8. **`app/register/page.tsx`** (new) — client page cloned from `app/login/page.tsx` (same styling/Russian copy), POSTing to `/api/auth/register`, redirecting to `/dashboard` on success. Add a "Создать аккаунт" link on `login/page.tsx` and back-link on register.

## Files to edit for identity (auth changes — flagged)

9. **`lib/session.ts`** — extend `SessionPayload` with an optional `sub` (username). `createSessionToken(secret, username?)` includes it; verification stays the same. Add a helper to read `sub` from a token. **Backward compatible:** existing tokens without `sub` remain valid.
10. **`lib/auth/currentUser.ts`** — if the token carries `sub`, look it up via `userStorage` and return `{ username, role }`; otherwise fall back to the env admin (current behavior). Keeps `app/api/auth/me/route.ts` working unchanged.
11. **`app/api/auth/login/route.ts`** — after the existing env-admin check fails, also try the user store (verify hashed password); on success issue a token with `sub`. Env admin path unchanged.
12. **`middleware.ts`** — add `register` to the public matcher exclusion (line 25) and the route to the public set, alongside `login`.

## Out of scope (unchanged)

`benchmark`, `favorites`, `feedback`, `jobs`, `overview`, `analyze`, `health/*` routes — these appear in the affected-files list but require **no change** for registration itself. They already sit behind middleware. (Per-user data scoping would be a separate, much larger task; I am **not** doing it under "smallest safe.")

## Validation / rollout
- `npm run db:init` is idempotent — safe to re-run for the new table.
- Local-fs backend works with zero config (`data/users.json`).
- Manual test: register → auto-login → `/api/auth/me` reflects the new username; env admin login still works; duplicate username → 409.
- Reversible: delete the new files, revert the `sub`/lookup additions; old identity-less sessions still validate.

---

## Decision points I assumed (please confirm or redirect)

1. **Registration model** — I assumed *full multi-user store*. Alternatives: single-account bootstrap (set up the one admin, no multi-user) or registration *requests* for admin approval (no auto-login). These produce very different plans.
2. **Password hashing** — I assumed `node:crypto` scrypt (no new dep) over adding bcrypt/argon2.
3. **Open vs. gated registration** — I assumed registration is open to anyone hitting the page. If it should be invite-only / first-user-only / admin-gated, the API and middleware change.
4. **Per-user data isolation** — I assumed **none** (all users share the existing data, like the admin does today). If each user needs isolated favorites/runs/etc., that is a large follow-up touching every storage call.

If any assumption is wrong — especially #1 or #4 — tell me and I'll rewrite the plan accordingly.

