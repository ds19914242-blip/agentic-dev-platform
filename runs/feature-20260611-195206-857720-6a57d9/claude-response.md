# Claude Response

The user dismissed the question, so I'll proceed with the safest sensible defaults and call them out explicitly: **Full working** auth wiring (the only option that ships a correct, non-exploitable feature) and **self-registration always creates role `"user"`** (env admin stays the sole admin; no schema or privilege-policy changes). Here is the plan.

---

# Implementation Plan — Task 010: Local registration page and API

## Context / current state (verified)

- **Storage is ready.** `userStorage` (`lib/storage/index.ts`) already exposes `getByUsername`, `create`, `count`, `list`, `getById`, `delete`, `updateRole`, for both local-fs (`LocalUserStorage`) and Postgres (`PostgresUserStorage`). The `users` table is already created by `scripts/dbInit.ts:95`. **No schema or storage changes needed.**
- **Password hashing is ready.** `lib/auth/password.ts` provides `hashPassword` / `verifyPassword` (scrypt). **No changes needed.**
- **Session supports embedded users.** `createSessionToken(secret, user)` (`lib/session.ts:74`) embeds `sub/username/role`; `readSessionPayload` decodes them. The plumbing exists but is unused.
- **The gaps:**
  1. No `/register` page and no `/api/auth/register` route.
  2. `app/api/auth/login/route.ts` validates **only** the env-var admin and creates an *anonymous* token (no user fields).
  3. `lib/auth/currentUser.ts` **ignores** the token's embedded user and always returns `{ username: APP_USERNAME, role: "admin" }`.
  4. `middleware.ts` matcher excludes `/login` but **not** `/register`, so a logged-out visitor to `/register` is bounced to `/login`.

## Design decisions (assumed — flag for review)

- Registration creates a `role: "user"` account and **auto-logs-in** by setting the session cookie with the embedded user (same cookie/flags as login).
- `currentUser` will **prefer the embedded session user**, falling back to the env admin only for legacy/anonymous tokens — this preserves the existing single-admin login and keeps `requireAdmin` working unchanged.
- Self-registration is open (anyone can create a `user` account). No email, no verification — matches the app's existing simplicity. Username uniqueness + 8-char min password mirror `/api/admin/users`.

---

## Changes

### 1. New file — `app/api/auth/register/route.ts` (the API)
Model it directly on `app/api/auth/login/route.ts` + the create logic in `app/api/admin/users/route.ts:31`.

- `export const runtime = "nodejs"; export const dynamic = "force-dynamic";`
- `POST(request)`:
  - Require `SESSION_SECRET` (else 500, same as login).
  - Parse JSON `{ username, password }`; 400 on bad JSON.
  - Validate: `username` non-empty (trimmed); `password.length >= 8`. Reuse the exact Russian error strings from `admin/users` route for consistency (`"Не указан логин."`, `"Пароль должен быть не короче 8 символов."`).
  - `hashPassword(password)` → `userStorage.create({ username, passwordHash, role: "user" })`.
  - Catch the `"already exists"` error from storage → 409 `"Пользователь с таким логином уже существует."` (storage throws `"Username already exists."`; match on `.includes("already exists")` exactly as the admin route does).
  - On success: `createSessionToken(secret, { id: user.id, username: user.username, role: user.role })`, set the `rss_session` cookie with the **same options as login** (`httpOnly`, `sameSite:"lax"`, `secure` in prod, `path:"/"`, `maxAge: SESSION_MAX_AGE_SECONDS`), return `{ ok: true }`.
- Lives under the `api/auth` prefix → already public in middleware (no matcher change needed for the API).

### 2. New file — `app/register/page.tsx` (the page)
Copy `app/login/page.tsx` and adapt (it's a `"use client"` form):
- Fields: username + password (add a confirm-password field, or keep single password to stay minimal — single password recommended for smallest change).
- Submit → `POST /api/auth/register`; on `res.ok` → `router.replace("/dashboard"); router.refresh()` (same as login, since we auto-login).
- Show `body.error` on failure; disable button while busy / when invalid (`password.length < 8`).
- Heading text in Russian to match the app (e.g. "Создать аккаунт"). Add a link back to `/login`.

### 3. `middleware.ts` — allow the `/register` page when logged out
Add `register` to the negative-lookahead in the matcher so the page is reachable for anonymous visitors:
```
"/((?!login|register|api/auth|api/health|_next/static|_next/image|favicon.ico).*)"
```
One-line change; fully reversible.

### 4. `lib/auth/currentUser.ts` — read the embedded session user
Replace the "always env admin" logic with: decode the payload via `readSessionPayload`; if it carries `username`/`role`, return those; otherwise fall back to the existing env-admin behavior (legacy/anonymous tokens). This is the **safety-critical** change — without it, a registered `user` would be reported as admin.
- Import `readSessionPayload` instead of (or alongside) `verifySessionToken`.
- Keep the signature/return type (`CurrentUser | null`) identical so `requireAdmin`, `/api/auth/me`, and `/api/admin/users` are unaffected.

### 5. `app/api/auth/login/route.ts` — let registered users sign in
So accounts created via registration (or `/admin/users`) can actually log in:
- First try `userStorage.getByUsername(username)` + `verifyPassword`. On match → `createSessionToken(secret, { id, username, role })`.
- Else fall back to the **existing** env-admin timing-safe check, creating a token embedding `{ username: APP_USERNAME, role: "admin" }` (or the anonymous token, to stay byte-for-byte minimal — but embedding keeps `currentUser` consistent).
- Preserve the constant-time comparison for the env-admin path; keep the same 401 message.

### 6. `app/login/page.tsx` — add a "Register" link (UX, optional but expected)
A small `<a href="/register">` under the form ("Нет аккаунта? Зарегистрируйтесь"). Pure additive.

---

## Files touched

| File | Change | Risk |
|---|---|---|
| `app/api/auth/register/route.ts` | **new** — registration API | low (additive) |
| `app/register/page.tsx` | **new** — registration UI | low (additive) |
| `middleware.ts` | +`register` in matcher | low, reversible |
| `lib/auth/currentUser.ts` | read embedded session user; env-admin fallback | **medium — auth read path** |
| `app/api/auth/login/route.ts` | validate DB users + embed user in token | **medium — auth** |
| `app/login/page.tsx` | add register link | low (additive) |

Files in the task's "affected" list that I do **not** plan to change (analyze, benchmark, favorites, feedback, health/db, admin/users) — they already consume `currentUser`/`requireAdmin` unchanged and need no edits; they appear to be auto-listed context.

## Verification
- `npm run typecheck` (script exists in `package.json`).
- Manual (local-fs backend, no DB needed): register a new user → lands on `/dashboard`; `GET /api/auth/me` returns `{ username, role: "user" }`; logout; log back in via `/login` with the new credentials; confirm `/admin/users` is **403** for that `user` while the env admin still gets in. Duplicate username → 409; short password → 400.
- Confirm legacy/existing sessions (anonymous tokens) still resolve to the env admin (back-comat via the `currentUser` fallback).

## Reversibility
Deleting the two new files and reverting the 4 one-spot edits restores current behavior exactly. No data migration, no schema change, no secrets/billing/deploy changes.

---

### ⚠️ Key uncertainties to confirm before coding
1. **Auth-wiring depth (items 4 & 5).** The task title is "registration page and API," but a register route in isolation is unsafe (privilege escalation) or non-functional given the current `currentUser`/`login`. I assumed the minimal *correct* wiring. If you want the literal narrowest diff (route+page only) despite the security/usability gap, drop items 4–6 — but I'd advise against it.
2. **Role policy.** Assumed every self-registration is `role: "user"`. The alternative (first registrant becomes `admin`) was offered; not chosen, so not included.
3. **Auto-login on register.** Assumed yes. If you prefer "create then redirect to /login," only the register route's tail and the page's redirect change.

This is plan-only — no files were modified. Let me know on the three points above (or just say "proceed") and I'll implement.

