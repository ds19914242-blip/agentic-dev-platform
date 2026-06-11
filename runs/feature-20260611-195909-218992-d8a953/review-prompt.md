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

Epic task: Task 011 — Create missing local registration route and page

# Approved Plan

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



# Implementation Response

# Claude Implementation Response

Type check passed with no errors. Implementation complete.

## Summary of changes

**Created (2):**
- `app/api/auth/register/route.ts` — public `POST /api/auth/register`. Mirrors the validation of `POST /api/admin/users` (JSON parse, non-empty username, password ≥ 8 chars, `already exists` → 409) but with **no admin gate** and **role hard-coded to `"user"`** (a client-supplied role is ignored, preventing self-promotion). Returns a sanitized user with no `passwordHash`.
- `app/register/page.tsx` — client registration page styled identically to the login page. On success it redirects to `/login` (no session is issued here); shows `body.error` on failure; links back to login.

**Edited (2):**
- `middleware.ts` — added `register` to the matcher's negative-lookahead so the `/register` *page* is reachable while unauthenticated (the `/api/auth/register` route was already public under `api/auth`).
- `app/login/page.tsx` — added a "Регистрация" link to `/register` (plus the `next/link` import).

**Verification:** `npx tsc --noEmit` passed clean.

## Risks

- **Known limitation (carried over from the plan):** registered users **cannot log in yet.** `app/api/auth/login/route.ts` and `lib/auth/currentUser.ts` still authenticate only the env-var admin and were deliberately left untouched (the rules forbid modifying auth unless explicitly required). Registration persists the user but does not make the account end-to-end functional. This should be tracked as a follow-up task (wire `login` to `userStorage.getByUsername` + `verifyPassword`, and resolve the session subject/role in `currentUser`).
- **Otherwise low risk:** changes are additive and reversible (delete the two new files, revert the one-token matcher addition and the login-page link). No schema, session, secrets, or deployment config touched.

Want me to extend this into the **registration + login wiring** variant so accounts work end-to-end?


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
   Generating static pages (0/21) ...
   Generating static pages (5/21) 
   Generating static pages (10/21) 
   Generating static pages (15/21) 
 ✓ Generating static pages (21/21)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    6.38 kB         214 kB
├ ○ /_not-found                          872 B          88.2 kB
├ ○ /admin/users                         2.48 kB        89.8 kB
├ ƒ /api/admin/users                     0 B                0 B
├ ƒ /api/admin/users/[id]                0 B                0 B
├ ƒ /api/analyze                         0 B                0 B
├ ƒ /api/auth/login                      0 B                0 B
├ ƒ /api/auth/logout                     0 B                0 B
├ ƒ /api/auth/me                         0 B                0 B
├ ƒ /api/auth/register                   0 B                0 B
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
├ ○ /collections                         3.2 kB         90.5 kB
├ ○ /dashboard                           1.89 kB          98 kB
├ ○ /feedback                            1.66 kB          89 kB
├ ○ /history                             151 B          87.5 kB
├ ○ /login                               1.5 kB         97.6 kB
├ ○ /profiles                            3.3 kB         90.6 kB
├ ○ /reading-list                        1.8 kB         89.1 kB
├ ○ /register                            1.54 kB        97.6 kB
├ ○ /reports                             2.63 kB        98.7 kB
├ ○ /rss                                 151 B          87.5 kB
├ ○ /rss/collections                     151 B          87.5 kB
├ ƒ /run/[id]                            926 B           215 kB
├ ○ /settings                            2.06 kB        89.4 kB
├ ○ /sources                             7.75 kB        95.1 kB
├ ○ /templates                           151 B          87.5 kB
└ ○ /workspace                           151 B          87.5 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/771-95e2dd6d11c2001c.js       31.7 kB
  ├ chunks/f3a82518-26a66ae169bcd6aa.js  53.6 kB
  └ other shared chunks (total)          1.95 kB


ƒ Middleware                             26.9 kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand


```

### STDERR

```text

```

