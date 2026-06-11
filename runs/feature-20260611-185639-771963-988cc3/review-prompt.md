# Review Implementation

Review whether the implementation satisfies the feature request.

Return ONLY valid JSON with this shape:

{
  "requirements_covered": true,
  "scope_creep": false,
  "architecture_risk": "low",
  "blocking_issues": [],
  "summary": ""
}

Rules:
- Be strict but practical.
- Do not invent issues.
- Mark requirements_covered=false only if the feature clearly was not implemented.
- Mark scope_creep=true if implementation changed unrelated areas.
- architecture_risk must be one of: low, medium, high.

# Feature Request

Epic task: Task 006 — Self-registration API and page

# Approved Plan

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



# Implementation Response

# Claude Implementation Response

Error: Reached max turns (15)

[WARNING] Claude reached max turns before final response.

# Validation Report

# Validation Result

## Overall Result

passed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build

  ▲ Next.js 14.2.35
  - Environments: .env

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
   Generating static pages (0/19) ...
   Generating static pages (4/19) 
   Generating static pages (9/19) 
   Generating static pages (14/19) 
 ✓ Generating static pages (19/19)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    6.38 kB         214 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ƒ /api/analyze                         0 B                0 B
├ ƒ /api/auth/login                      0 B                0 B
├ ƒ /api/auth/logout                     0 B                0 B
├ ƒ /api/auth/me                         0 B                0 B
├ ƒ /api/benchmark                       0 B                0 B
├ ƒ /api/favorites                       0 B                0 B
├ ƒ /api/favorites/[id]                  0 B                0 B
├ ƒ /api/feedback                        0 B                0 B
├ ƒ /api/health                          0 B                0 B
├ ƒ /api/health/db                       0 B                0 B
├ ƒ /api/jobs/[jobId]                    0 B                0 B
├ ƒ /api/overview                        0 B                0 B
├ ƒ /api/profiles                        0 B                0 B
├ ƒ /api/profiles/[id]                   0 B                0 B
├ ƒ /api/report/[id]/docx                0 B                0 B
├ ƒ /api/report/[id]/json                0 B                0 B
├ ƒ /api/report/[id]/markdown            0 B                0 B
├ ƒ /api/report/[id]/pdf                 0 B                0 B
├ ƒ /api/rss/collect                     0 B                0 B
├ ƒ /api/rss/collections                 0 B                0 B
├ ƒ /api/rss/collections/[id]            0 B                0 B
├ ƒ /api/rss/sources                     0 B                0 B
├ ƒ /api/rss/sources/[id]                0 B                0 B
├ ƒ /api/rss/summarize                   0 B                0 B
├ ƒ /api/rss/test                        0 B                0 B
├ ƒ /api/runs                            0 B                0 B
├ ƒ /api/runs/[id]                       0 B                0 B
├ ƒ /api/settings                        0 B                0 B
├ ƒ /api/upload                          0 B                0 B
├ ○ /benchmark                           2.5 kB         92.6 kB
├ ○ /collections                         3.21 kB        90.5 kB
├ ○ /dashboard                           1.89 kB        97.9 kB
├ ○ /feedback                            1.66 kB          89 kB
├ ○ /history                             152 B          87.5 kB
├ ○ /login                               1.41 kB        88.7 kB
├ ○ /profiles                            3.3 kB         90.6 kB
├ ○ /reading-list                        1.8 kB         89.1 kB
├ ○ /reports                             2.63 kB        98.7 kB
├ ○ /rss                                 152 B          87.5 kB
├ ○ /rss/collections                     152 B          87.5 kB
├ ƒ /run/[id]                            936 B           215 kB
├ ○ /settings                            2.06 kB        89.4 kB
├ ○ /sources                             7.75 kB        95.1 kB
├ ○ /templates                           152 B          87.5 kB
└ ○ /workspace                           152 B          87.5 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/117-c2e8725fecde5126.js       31.7 kB
  ├ chunks/fd9d1056-307a36020502e7d7.js  53.6 kB
  └ other shared chunks (total)          1.95 kB


ƒ Middleware                             26.9 kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand


```

### STDERR

```text

```

