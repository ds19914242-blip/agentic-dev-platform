# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 010 — Add local registration page and API

## Planner Input

# Implementation Plan

## Summary

Add a self-service local **registration** flow: a public `POST /api/auth/register` endpoint that creates a `UserRecord` (hashed password) and signs the user in, plus a public `/register` page mirroring the existing login UI. Nearly all backend primitives already exist — `UserStorage` (Local + Postgres), `hashPassword`, and `createSessionToken(secret, user)` with embeddable `{sub, username, role}` — so this is mostly wiring a new route + page and opening them in middleware.

## Files To Inspect

- `lib/session.ts` — `createSessionToken(secret, user)`, `SESSION_COOKIE`, `SESSION_MAX_AGE_SECONDS` (reuse for setting the cookie). ✓ already read
- `lib/auth/password.ts` — `hashPassword`. ✓
- `lib/storage/types.ts` — `UserStorage` / `UserRecord` (`create`, `getByUsername`, `count`). ✓
- `lib/storage/local.ts` + `lib/storage/postgres.ts` — confirm `create` throws/`already exists` on duplicate username (the admin route relies on this; register must too).
- `app/api/auth/login/route.ts` — cookie-set pattern + Russian error strings to match. ✓
- `app/api/admin/users/route.ts` — validation pattern (username trim, password ≥ 8, role set, 409 on duplicate) to mirror. ✓
- `app/login/page.tsx` — UI structure to copy for the register page. ✓
- `middleware.ts` — matcher excludes `login`, `api/auth`, `api/health`; `/register` page must be added to the negative lookahead. ✓
- `lib/auth/currentUser.ts` — **key gap** (see Risks): currently returns env `APP_USERNAME`/`"admin"` and ignores session user fields.

## Implementation Steps

1. **`app/api/auth/register/route.ts`** (new, `runtime = "nodejs"`, `dynamic = "force-dynamic"`):
   - Parse JSON `{ username, password }`; mirror validation from the admin POST (trim username non-empty, password ≥ 8 chars). Reject invalid JSON with 400.
   - Reject duplicate via `userStorage.getByUsername` (or catch the `already exists` error from `create`) → 409 with `"Пользователь с таким логином уже существует."`.
   - Assign role: default `"user"`; optionally make the **first** user `"admin"` via `userStorage.count() === 0` (decision — see Risks).
   - `hashPassword(password)` → `userStorage.create({ username, passwordHash, role })`.
   - Sign in immediately: `createSessionToken(secret, { id, username, role })`; set `SESSION_COOKIE` with the same cookie options as login. Return `{ ok: true }`. Guard on missing `SESSION_SECRET` → 500.
2. **`app/register/page.tsx`** (new, client component): copy `login/page.tsx`, POST to `/api/auth/register`, on success `router.replace("/dashboard")` + `router.refresh()`. Add a "уже есть аккаунт? Войти" link to `/login`.
3. **`app/login/page.tsx`**: add a "Зарегистрироваться" link to `/register`.
4. **`middleware.ts`**: add `register` to the matcher negative lookahead so the page is reachable while logged out (`(?!login|register|api/auth|...)`). The API is already public under `api/auth`.

## Validation Steps

- `npm run build` / typecheck (`tsc`) — no type errors on new files.
- Manual (local-fs backend): visit `/register` while logged out → register → redirected to `/dashboard` with a session cookie set.
- Duplicate username → 409 with the expected message.
- Password < 8 chars and empty username → 400.
- Confirm `data/users.json` (local) or `users` table (postgres) receives a record with a `scrypt$…` hash, never plaintext.

## Risks

- **Login/currentUser do not recognize registered users (highest risk).** `POST /api/auth/login` validates only against `APP_USERNAME`/`APP_PASSWORD` env vars, and `currentUser` returns `{ username: APP_USERNAME, role: "admin" }` for *any* valid session — ignoring the embedded `sub/username/role`. Consequences: (a) a registered user can sign in at registration time, but **cannot log back in** after logout; (b) once logged in, they'd resolve as the env admin. Decide scope: either Task 010 is registr

## plan

# Implementation Plan

## Summary

Add a self-service local **registration** flow: a public `POST /api/auth/register` endpoint that creates a `UserRecord` (hashed password) and signs the user in, plus a public `/register` page mirroring the existing login UI. Nearly all backend primitives already exist — `UserStorage` (Local + Postgres), `hashPassword`, and `createSessionToken(secret, user)` with embeddable `{sub, username, role}` — so this is mostly wiring a new route + page and opening them in middleware.

## Files To Inspect

- `lib/session.ts` — `createSessionToken(secret, user)`, `SESSION_COOKIE`, `SESSION_MAX_AGE_SECONDS` (reuse for setting the cookie). ✓ already read
- `lib/auth/password.ts` — `hashPassword`. ✓
- `lib/storage/types.ts` — `UserStorage` / `UserRecord` (`create`, `getByUsername`, `count`). ✓
- `lib/storage/local.ts` + `lib/storage/postgres.ts` — confirm `create` throws/`already exists` on duplicate username (the admin route relies on this; register must too).
- `app/api/auth/login/route.ts` — cookie-set pattern + Russian error strings to match. ✓
- `app/api/admin/users/route.ts` — validation pattern (username trim, password ≥ 8, role set, 409 on duplicate) to mirror. ✓
- `app/login/page.tsx` — UI structure to copy for the register page. ✓
- `middleware.ts` — matcher excludes `login`, `api/auth`, `api/health`; `/register` page must be added to the negative lookahead. ✓
- `lib/auth/currentUser.ts` — **key gap** (see Risks): currently returns env `APP_USERNAME`/`"admin"` and ignores session user fields.

## Implementation Steps

1. **`app/api/auth/register/route.ts`** (new, `runtime = "nodejs"`, `dynamic = "force-dynamic"`):
   - Parse JSON `{ username, password }`; mirror validation from the admin POST (trim username non-empty, password ≥ 8 chars). Reject invalid JSON with 400.
   - Reject duplicate via `userStorage.getByUsername` (or catch the `already exists` error from `create`) → 409 with `"Пользователь с таким логином уже существует."`.
   - Assign role: default `"user"`; optionally make the **first** user `"admin"` via `userStorage.count() === 0` (decision — see Risks).
   - `hashPassword(password)` → `userStorage.create({ username, passwordHash, role })`.
   - Sign in immediately: `createSessionToken(secret, { id, username, role })`; set `SESSION_COOKIE` with the same cookie options as login. Return `{ ok: true }`. Guard on missing `SESSION_SECRET` → 500.
2. **`app/register/page.tsx`** (new, client component): copy `login/page.tsx`, POST to `/api/auth/register`, on success `router.replace("/dashboard")` + `router.refresh()`. Add a "уже есть аккаунт? Войти" link to `/login`.
3. **`app/login/page.tsx`**: add a "Зарегистрироваться" link to `/register`.
4. **`middleware.ts`**: add `register` to the matcher negative lookahead so the page is reachable while logged out (`(?!login|register|api/auth|...)`). The API is already public under `api/auth`.

## Validation Steps

- `npm run build` / typecheck (`tsc`) — no type errors on new files.
- Manual (local-fs backend): visit `/register` while logged out → register → redirected to `/dashboard` with a session cookie set.
- Duplicate username → 409 with the expected message.
- Password < 8 chars and empty username → 400.
- Confirm `data/users.json` (local) or `users` table (postgres) receives a record with a `scrypt$…` hash, never plaintext.

## Risks

- **Login/currentUser do not recognize registered users (highest risk).** `POST /api/auth/login` validates only against `APP_USERNAME`/`APP_PASSWORD` env vars, and `currentUser` returns `{ username: APP_USERNAME, role: "admin" }` for *any* valid session — ignoring the embedded `sub/username/role`. Consequences: (a) a registered user can sign in at registration time, but **cannot log back in** after logout; (b) once logged in, they'd resolve as the env admin. Decide scope: either Task 010 is registration-only (flag login integration as a follow-up — likely Task 011), or extend `currentUser`/login to read session user

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 010 — Add local registration page and API

## Based On Plan

# Implementation Plan

## Summary

Add a self-service local **registration** flow: a public `POST /api/auth/register` endpoint that creates a `UserRecord` (hashed password) and signs the user in, plus a public `/register` page mirroring the existing login UI. Nearly all backend primitives already exist — `UserStorage` (Local + Postgres), `hashPassword`, and `createSessionToken(secret, user)` with embeddable `{sub, username, role}` — so this is mostly wiring a new route + page and opening them in middleware.

## Files To Inspect

- `lib/session.ts` — `createSessionToken(secret, user)`, `SESSION_COOKIE`, `SESSION_MAX_AGE_SECONDS` (reuse for setting the cookie). ✓ already read
- `lib/auth/password.ts` — `hashPassword`. ✓
- `lib/storage/types.ts` — `UserStorage` / `UserRecord` (`create`, `getByUsername`, `count`). ✓
- `lib/storage/local.ts` + `lib/storage/postgres.ts` — confirm `create` throws/`already exists` on duplicate username (the admin route relies on this; register must too).
- `app/api/auth/login/route.ts` — cookie-set pattern + Russian error strings to match. ✓
- `app/api/admin/users/route.ts` — validation pattern (username trim, password ≥ 8, role set, 409 on duplicate) to mirror. ✓
- `app/login/page.tsx` — UI structure to copy for the register page. ✓
- `middleware.ts` — matcher excludes `login`, `api/auth`, `api/health`; `/register` page must be added to the negative lookahead. ✓
- `lib/auth/currentUser.ts` — **key gap** (see Risks): currently returns env `APP_USERNAME`/`"admin"` and ignores session user fields.

## Implementation Steps

1. **`app/api/auth/register/route.ts`** (new, `runtime = "nodejs"`, `dynamic = "force-dynamic"`):
   - Parse JSON `{ username, password }`; mirror validation from the admin POST (trim username non-empty, password ≥ 8 chars). Reject invalid JSON with 400.
   - Reject duplicate via `userStorage.getByUsername` (or catch the `already exists` error from `create`) → 409 with `"Пользователь с таким логином уже существует."`.
   - Assign role: default `"user"`; optionally make the **first** user `"admin"` via `userStorage.count() === 0` (decision — see Risks).
   - `hashPassword(password)` → `userStorage.create({ username, passwordHash, role })`.
   - Sign in immediately: `createSessionToken(secret, { id, username, role })`; set `SESSION_COOKIE` with the same cookie options as login. Return `{ ok: true }`. Guard on missing `SESSION_SECRET` → 500.
2. **`app/register/page.tsx`** (new, client component): copy `login/page.tsx`, POST to `/api/auth/register`, on success `router.replace("/dashboard")` + `router.refresh()`. Add a "уже есть аккаунт? Войти" link to `/login`.
3. **`app/login/page.tsx`**: add a "Зарегистрироваться" link to `/register`.
4. **`middleware.ts`**: add `register` to the matcher negative lookahead so the page is reachable while logged out (`(?!login|register|api/auth|...)`). The API is already public under `api/auth`.

## Validation Steps

- `npm run build` / typecheck (`tsc`) — no type errors on new files.
- Manual (local-fs backend): visit `/register` while logged out → register → redirected to `/dashboard` with a session cookie set.
- Duplicate username → 409 with the expected message.
- Password < 8 chars and empty username → 400.
- Confirm `data/users.json` (local) or `users` table (postgres) receives a record with a `scrypt$…` hash, never plaintext.

## Risks

- **Login/currentUser do not recognize registered users (highest risk).** `POST /api/auth/login` validates only against `APP_USERNAME`/`APP_PASSWORD` env vars, and `currentUser` returns `{ username: APP_USERNAME, role: "admin" }` for *any* valid session — ignoring the embedded `sub/username/role`. Consequences: (a) a registered user can sign in at registration time, but **cannot log back in** after logout; (b) once logged in, they'd resolve as the env admin. Decide scope: either Task 010 is registration-only (
