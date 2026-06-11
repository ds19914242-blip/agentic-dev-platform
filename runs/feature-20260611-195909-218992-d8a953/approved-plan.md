# Approved Plan

The question was dismissed, so I'll proceed with the default that best fits the stated rules ("smallest safe implementation," "do not modify auth unless explicitly required," "keep changes small and reversible"): **registration-only**, with the login-integration gap documented prominently as a known limitation. Here is the plan.

---

# Implementation Plan — Task 011: Local registration route and page

## Context & findings

The repo already has all user-storage plumbing, but no self-service registration entry point:

| Piece | Status |
|---|---|
| `UserStorage` (local-fs + Postgres) with `create`, `getByUsername`, `count` | ✅ exists (`lib/storage/`) |
| `hashPassword` / `verifyPassword` (scrypt) | ✅ exists (`lib/auth/password.ts`) |
| Admin-gated user creation `POST /api/admin/users` | ✅ exists |
| **Public `POST /api/auth/register` route** | ❌ **missing** |
| **`/register` page** | ❌ **missing** |
| Login wiring for storage users | ❌ absent (login + `currentUser` only know the env-var admin) |

The login route and `currentUser` authenticate **only** the env-var admin; `getByUsername`/`verifyPassword`/`count` are currently unused. This plan creates the missing registration route + page. **It deliberately does not modify login/`currentUser`/session** (per the rules). See "Known limitation" below.

## Files to create (2) + 1 small edit

### 1. `app/api/auth/register/route.ts` (new)
Public registration endpoint, mirroring the validation in `app/api/admin/users/route.ts` (lines 30–73) but without the admin gate.

- `export const runtime = "nodejs"; export const dynamic = "force-dynamic";`
- `POST(request)`:
  - Parse JSON body `{ username, password }`; 400 `"Некорректный JSON."` on parse failure (match existing wording).
  - Trim username; require non-empty → 400 `"Не указан логин."`.
  - Require `password.length >= 8` → 400 `"Пароль должен быть не короче 8 символов."`.
  - Role: **always `"user"`** — never accept a client-supplied role (prevents self-promotion to admin). 
  - `passwordHash = await hashPassword(password)`, then `userStorage.create({ username, passwordHash, role: "user" })`.
  - On `"already exists"` error → 409 `"Пользователь с таким логином уже существует."` (same mapping as admin route, lines 63–70).
  - On success → return sanitized user `{ id, username, role, createdAt }` (reuse the `sanitize` shape; do **not** return `passwordHash`).
- Imports: `userStorage` from `lib/storage/index.js`, `hashPassword` from `lib/auth/password.js`, `UserRecord` type, `NextResponse`.
- Use the same relative import depth as `app/api/auth/login/route.ts` (`../../../../lib/...`).

### 2. `app/register/page.tsx` (new)
Client component mirroring `app/login/page.tsx` (same Tailwind classes / card layout / Russian copy for consistency).

- `"use client"`, `useState` for `username`, `password`, `error`, `busy`.
- Submit → `POST /api/auth/register`. On success, redirect to `/login` (NOT `/dashboard`), since registration does not establish a session under this scope. Show a brief success state or route straight to `/login`.
- On error, display `body.error` (same red error box pattern as login).
- Add a link back to `/login` ("Уже есть аккаунт? Войти"), and add a "Регистрация" link on the login page pointing to `/register` (small addition to `app/login/page.tsx`).
- Header copy e.g. "Создать аккаунт".

### 3. `middleware.ts` (one-line edit — required for the page to be reachable)
Currently the matcher (line 25) redirects everything except `login|api/auth|api/health|_next…` to `/login`. `/api/auth/register` is **already public** (covered by `api/auth`), but the `/register` **page** is not — an unauthenticated visitor would be bounced to `/login`. Add `register` to the negative-lookahead group:

```
"/((?!login|register|api/auth|api/health|_next/static|_next/image|favicon.ico).*)"
```

This is the minimal, reversible auth-adjacent change strictly required to make a self-service registration page usable.

## What is NOT changed
- `lib/session.ts`, `lib/auth/currentUser.ts`, `app/api/auth/login/route.ts` — untouched. No session is issued at registration.
- No DB schema, secrets, billing, or deployment config.
- The 12 affected API routes listed in the task are **context only**; none needs modification.

## ⚠️ Known limitation (flag for reviewer / follow-up task)
After this change, a user can register and be persisted, but **cannot log in**, because `login` and `currentUser` still recognize only the env-var admin. Making registered users able to sign in requires editing `app/api/auth/login/route.ts` (look up `userStorage.getByUsername` + `verifyPassword`, embed user in the session via `createSessionToken(secret, user)`) and `lib/auth/currentUser.ts` (resolve the session's `sub`/`role` instead of hard-coding the env admin). That touches auth and is intentionally **out of scope** here (the rules say not to modify auth unless explicitly required). Recommend tracking it as the next task. *If you want registration to be end-to-end functional in this task instead, say so and I'll extend the plan to include the login wiring.*

## Verification steps
1. `npm run typecheck` — must pass.
2. `npm run dev`; unauthenticated, navigate to `/register` (should render, not redirect).
3. Submit valid `{username, password>=8}` → 200, user appears in local-fs `data/users.json` (or via `/api/admin/users` GET as admin); confirm response has no `passwordHash`.
4. Re-submit same username → 409. Submit short password → 400. Submit role override in body → role is still `"user"`.

## Risk / reversibility
Low. Two additive files plus a one-token middleware matcher addition. Fully reversible by deleting the two files and reverting the matcher line.

---

Per the task ("Do not modify files. Stop after the plan."), I've made no changes. Let me know if you'd like the **registration + login wiring** variant instead.

