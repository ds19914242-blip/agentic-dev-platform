# Claude Response

I now have a complete picture of the codebase. Let me present the implementation plan.

## Context: What I Found

**Auth model (important).** The app runs **two partially-built auth systems**:

1. **Active:** A single hard-coded admin from env vars (`APP_USERNAME`/`APP_PASSWORD`). `POST /api/auth/login` (`app/api/auth/login/route.ts`) checks these; the session cookie (`lib/session.ts`) is **stateless** — it stores only `authenticated:true` + expiry, no user identity. `currentUser()` (`lib/auth/currentUser.ts`) therefore always resolves an authenticated request to `{ username: APP_USERNAME, role: "admin" }`.
2. **Dormant (added by Task 006, commit `3eb2cca`):** A `users` table + `UserStorage` (`getByUsername`, `create`, `count`), scrypt hashing (`lib/auth/password.ts`). **Not wired into login or session** — and no register route/page exists yet (Task 006 only landed the `lib` layer).

The `users` table already exists in `scripts/dbInit.ts` (id, username, password_hash, role, created_at) with a unique username index — **no schema change is needed.**

**Conventions:** Routes use `runtime="nodejs"`, `dynamic="force-dynamic"`, `NextResponse.json`, Russian-language error messages. Storage is selected in `lib/storage/index.ts` (Postgres vs local-fs). UI pages are `"use client"`, fetch JSON, use `card`/`btn-primary`/`chip` classes; `NavBar.tsx` holds a flat `LINKS` array.

---

## ⚠️ One uncertainty to flag (non-blocking)

Users created through this admin panel **cannot log in yet** — login is still env-only and the session carries no identity. This is expected mid-epic (Task 007 builds the management surface on top of Task 006's storage; a later task presumably wires `UserStorage` into login). My plan builds the management API + page against `UserStorage` as-is and does **not** touch login/session/middleware (per the "don't modify auth" rule). If you intended Task 007 to *also* switch login over to the user table, that's a larger change — tell me and I'll re-plan.

---

## Implementation Plan — Task 007: Admin user management API & page

### 1. Extend `UserStorage` (additive only — no DDL)

**`lib/storage/types.ts`** — add three methods to the `UserStorage` interface:
```ts
list(): Promise<UserRecord[]>;
getById(id: string): Promise<UserRecord | undefined>;   // for delete/update validation
delete(id: string): Promise<void>;
updateRole(id: string, role: string): Promise<UserRecord | undefined>;
```
(`updateRole` is the only "edit" operation; password reset is intentionally out of scope to stay minimal.)

**`lib/storage/local.ts`** — `LocalUserStorage`: implement `list` (read `users.json`, newest-first), `getById`, `delete` (filter + rewrite), `updateRole` (find + patch + rewrite), mirroring `LocalFavoriteStorage`.

**`lib/storage/postgres.ts`** — `PostgresUserStorage`: implement the same with `safeRead`/`safeWrite`:
- `list` → `SELECT * FROM users ORDER BY created_at DESC` → `rowToUser`
- `getById` → `SELECT … WHERE id = $1`
- `delete` → `DELETE FROM users WHERE id = $1`
- `updateRole` → `UPDATE users SET role = $2 WHERE id = $1`, then re-select

No `index.ts` change required (it already exports `userStorage`).

### 2. Admin gate helper

**New `lib/auth/requireAdmin.ts`** — wraps `currentUser(cookies())`; returns the user if `role === "admin"`, else `null`. Routes translate `null` → `401`/`403`. Keeps role logic in one place and ready for when real roles arrive.

### 3. API routes (new)

**`app/api/admin/users/route.ts`** (`runtime="nodejs"`, `dynamic="force-dynamic"`):
- `GET` — admin-gate; return `userStorage.list()` **mapped to strip `passwordHash`** (`{ id, username, role, createdAt }`).
- `POST` — admin-gate; parse `{ username, password, role }`; validate (non-empty username, password length ≥ 8, role ∈ `{"admin","user"}`); reject duplicate (catch `create`'s "Username already exists" → `409`); `hashPassword(password)` → `userStorage.create(...)`; return sanitized user. Russian error messages to match existing routes.

**`app/api/admin/users/[id]/route.ts`** (mirrors `app/api/favorites/[id]/route.ts`):
- `PATCH` — admin-gate; `{ role }` → validate → `updateRole`; `404` if not found.
- `DELETE` — admin-gate; **guard against self-delete** (compare to `currentUser`); `404` if not found, else `{ ok: true }`.

### 4. Admin page (new)

**`app/admin/users/page.tsx`** — `"use client"`, modeled on `app/reading-list/page.tsx`:
- Load `GET /api/admin/users`; render a `card` table/list (username, role badge, created date).
- "Add user" form (username, password, role select) → `POST`; optimistic refresh; show server error in the red error box pattern from `login/page.tsx`; use `useToast` for success.
- Per-row role toggle (`PATCH`) and Remove button (`DELETE`), disabling Remove on the current admin's own row.
- Russian UI labels to match the app (e.g. «Пользователи», «Добавить», «Удалить», «Роль»).

Middleware already protects `/admin/**` via the session cookie; the API enforces the admin role as the real guard.

### 5. Navigation

**`components/NavBar.tsx`** — add `{ href: "/admin/users", label: "Пользователи" }` to `LINKS` (and `/admin/users` is prefix-matched, so no `EXACT` change). *(Optional: conditionally hide if not admin — but since the only logged-in user is always admin today, I'll add it unconditionally to keep it minimal. Tell me if you want it gated.)*

### 6. Verification (no test framework changes)
- `npm run build` / typecheck to confirm types.
- Manual: local-fs backend (`users.json`) — create/list/role-change/delete; confirm `passwordHash` never leaves the API; confirm self-delete is blocked; confirm a logged-out request to `/api/admin/users` → 401.

---

### Files touched
| File | Change |
|---|---|
| `lib/storage/types.ts` | +4 methods on `UserStorage` |
| `lib/storage/local.ts` | implement in `LocalUserStorage` |
| `lib/storage/postgres.ts` | implement in `PostgresUserStorage` |
| `lib/auth/requireAdmin.ts` | **new** gate helper |
| `app/api/admin/users/route.ts` | **new** GET/POST |
| `app/api/admin/users/[id]/route.ts` | **new** PATCH/DELETE |
| `app/admin/users/page.tsx` | **new** UI |
| `components/NavBar.tsx` | +1 nav link |

**Not touched:** login/logout/session/middleware, DB schema/`dbInit.ts`, billing, secrets, deploy config. All changes are additive and reversible. The 12 "affected files" in the task were inspection targets for convention-matching; only `NavBar` + the new files actually change.

Per plan_only mode, I've made no edits. Want me to proceed with this, adjust scope (e.g. add password-reset, role-gate the nav link, or also wire login to the user table), or drill into any step?

