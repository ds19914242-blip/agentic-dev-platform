I now have a clear picture of the architecture. Here's the decomposition.

# Epic

## Summary

The app currently supports a **single hard-coded admin account**: credentials come from `APP_USERNAME` / `APP_PASSWORD` env vars (`app/api/auth/login/route.ts`), and the session is a stateless HMAC-signed cookie (`lib/session.ts`) that encodes only `authenticated=true` + an expiry — it carries no user identity. `middleware.ts` gates every route on that cookie. Persistence already follows a clean "no-DB" pattern: file-backed stores in `lib/storage/local.ts` writing JSON under `data/`, behind interfaces in `lib/storage/types.ts`, registered in `lib/storage/index.ts`. There is even a `DEFAULT_OWNER = "local-user"` placeholder and unused `ownerId` fields on `RssSource` / `RssCollection` anticipating multi-user.

This epic adds a **multi-user account system with no database**: a file-backed user store with hashed passwords, a session token that carries the logged-in user's identity, login validated against the store, a current-user endpoint, UI surfacing of the active account, self-registration and admin user management, and (last, highest-risk) per-account data scoping via the existing `ownerId` fields.

## Assumptions

- "Without DB" = persist users as a JSON file under `data/` (e.g. `data/users.json`) using the same local-fs pattern as the other stores. No Postgres user backend is required.
- Passwords are hashed (salted `scrypt`/`pbkdf2` from `node:crypto`) — never stored in plaintext. Existing session signing/HMAC design is reused unchanged for the cookie.
- A `role` field (`admin` | `user`) exists from the start; the first/bootstrap account is `admin`, seeded from the existing `APP_USERNAME`/`APP_PASSWORD` env vars when the store is empty (preserves current login on upgrade).
- Self-registration is **enabled** but creates only non-admin `user` accounts; admin accounts are created/managed by an existing admin. (If the product wants invite-only signup, drop Task 006 — nothing else depends on it.)
- Per-user data isolation (Tasks 008–009) is desired but is the riskiest part; it is sequenced last and split so the core account system ships first and independently.
- UI strings follow the existing Russian-language convention used across the app.

## Task List

### Task 001 — File-based user store with hashed passwords

**Goal:** Introduce a no-DB user store that persists accounts to a JSON file with salted password hashing, plus a one-time bootstrap of the admin account from existing env vars.
**Scope:** Define a `User` type (`id`, `username`, `passwordHash`, `salt`, `role`, `createdAt`) and `UserStorage` interface; implement `LocalUserStorage` (writes `data/users.json`, with `create`, `getByUsername`, `getById`, `list`, `delete`, and a password `verify` helper using `node:crypto` scrypt). Register `userStorage` in the storage index. On first access with an empty store, seed an `admin` user from `APP_USERNAME`/`APP_PASSWORD` if present.
**Suggested files:** `lib/storage/types.ts`, `lib/storage/local.ts`, `lib/storage/index.ts`, new `lib/auth/password.ts` (or inline hashing in the store).
**Acceptance criteria:** `userStorage` is exported and instantiable without opening any DB connection; passwords are stored only as salt+hash; creating then verifying a user round-trips; duplicate usernames are rejected; bootstrap seeds the admin once and is idempotent; `tsc` passes.
**Risk:** medium

## Depends On

_None_

### Task 002 — Encode user identity in the session token

**Goal:** Extend the stateless session cookie to carry the authenticated user's id/username/role instead of only `authenticated=true`, keeping signing and verification backward-compatible.
**Scope:** Add `sub` (userId), `username`, and `role` to `SessionPayload`; update `createSessionToken` to accept a user; add a `readSessionPayload(token, secret)` that returns the decoded, verified payload (or `null`). Keep `verifySessionToken` working (boolean) so `middleware.ts` needs no change. Tolerate old-format tokens gracefully (treated as unauthenticated or anonymous).
**Suggested files:** `lib/session.ts`.
**Acceptance criteria:** A token created for a user verifies and decodes back to that user's id/username/role; tampered tokens fail; expired tokens fail; existing boolean `verifySessionToken` behavior preserved; `tsc` passes.
**Risk:** low

## Depends On

_None_

### Task 003 — Authenticate login against the user store

**Goal:** Replace the single env-var credential check with lookup + password verification against the user store, issuing an identity-bearing session.
**Scope:** Update `POST /api/auth/login` to fetch the user by username from `userStorage`, verify the password hash in constant time, and on success call the new `createSessionToken(user, secret)`. Preserve the existing cookie attributes, error messages, and 500-when-unconfigured behavior (now keyed on `SESSION_SECRET`).
**Suggested files:** `app/api/auth/login/route.ts`.
**Acceptance criteria:** Valid stored credentials log in and set an identity session cookie; invalid credentials return 401 with the existing Russian error; the seeded admin (from Task 001) can still log in with the env credentials; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-002

### Task 004 — Current-user resolution helper and `/api/auth/me`

**Goal:** Provide a server helper to resolve the logged-in user from the request and an endpoint clients can call to learn who they are.
**Scope:** Add a `currentUser(cookies/secret)` helper that reads the session cookie, decodes the payload (Task 002), and loads the user from `userStorage` (Task 001). Add `GET /api/auth/me` returning `{ username, role }` (or 401). Add `api/auth/me` to public-or-authed handling as appropriate (it lives under the already-public `api/auth` matcher prefix, so confirm it 401s cleanly when unauthenticated).
**Suggested files:** new `lib/auth/currentUser.ts`, new `app/api/auth/me/route.ts`.
**Acceptance criteria:** Authenticated request to `/api/auth/me` returns the user's username/role; unauthenticated request returns 401; helper is reusable by other route handlers; `tsc` passes.
**Risk:** low

## Depends On

task-001, task-002

### Task 005 — Surface the active account in the NavBar

**Goal:** Show the logged-in username in the header next to the existing logout button.
**Scope:** Fetch `/api/auth/me` from the client `NavBar` and render the username (with a graceful fallback while loading / if it fails). No change to logout behavior.
**Suggested files:** `components/NavBar.tsx`.
**Acceptance criteria:** When logged in, the NavBar displays the current username; logout still works and redirects to `/login`; no hydration warnings; `tsc` passes.
**Risk:** low

## Depends On

task-004

### Task 006 — Self-registration API and page

**Goal:** Let new users create a (non-admin) account and land logged in.
**Scope:** Add `POST /api/auth/register` that validates input, rejects duplicate usernames, creates a `user`-role account via `userStorage`, and sets an identity session. Add a `/register` page mirroring the login page's styling with a link between the two. Add `register` to the public paths in the `middleware.ts` matcher so the page and endpoint are reachable while logged out.
**Suggested files:** new `app/api/auth/register/route.ts`, new `app/register/page.tsx`, `middleware.ts`, `app/login/page.tsx` (add link).
**Acceptance criteria:** Registering a fresh username creates the account, logs in, and redirects to `/dashboard`; duplicate username returns a clear error; new accounts get `role: "user"`; `/register` is reachable while unauthenticated; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-002

### Task 007 — Admin user management API and page

**Goal:** Give admins a UI to list, create, and delete accounts.
**Scope:** Add `GET/POST /api/users` and `DELETE /api/users/[id]`, each gated by `currentUser().role === "admin"` (403 otherwise). Add an `/app/users` page listing accounts with create (incl. role selection) and delete actions; prevent deleting the last admin / self-lockout. Add a NavBar link visible only to admins (optional, can reuse the `/api/auth/me` role).
**Suggested files:** new `app/api/users/route.ts`, new `app/api/users/[id]/route.ts`, new `app/users/page.tsx`, optionally `components/NavBar.tsx`.
**Acceptance criteria:** Admin can list/create/delete users; non-admins get 403 from the APIs and cannot see the page's controls; deleting the last admin is blocked; passwords are hashed on create; `tsc` passes.
**Risk:** medium

## Depends On

task-001, task-004

### Task 008 — Scope RSS sources and collections to the active user

**Goal:** Replace the `DEFAULT_OWNER` placeholder so each account only sees and manages its own RSS sources and collections.
**Scope:** In the RSS source/collection route handlers (and `lib/storage/rss.ts` if needed), resolve `currentUser()` and set `ownerId` on create, and filter `list`/`get`/`update`/`delete` by the current user's id. Provide a back-compat path so pre-existing records (owned by `local-user`) remain visible to the admin or are migrated.
**Suggested files:** `app/api/rss/sources/route.ts`, `app/api/rss/sources/[id]/route.ts`, `app/api/rss/collections/route.ts`, `app/api/rss/collections/[id]/route.ts`, `lib/storage/rss.ts`.
**Acceptance criteria:** A user sees only their own sources/collections; cannot read/modify another user's records (404/403); newly created records carry the creator's `ownerId`; legacy `local-user` records are handled per the chosen back-compat rule; `tsc` passes.
**Risk:** high

## Depends On

task-004

### Task 009 — Scope favorites and feedback to the active user

**Goal:** Make the reading list (favorites) and relevance feedback per-account rather than global.
**Scope:** Add an owner field to `FavoriteArticle` / `Feedback` (and their storage interfaces), set it from `currentUser()` on create, and filter `list`/`update`/`delete` by the current user in the favorites/feedback route handlers. Keep legacy unowned records handled gracefully (e.g. visible to admin or migrated).
**Suggested files:** `lib/storage/types.ts`, `lib/storage/local.ts`, `app/api/favorites/route.ts`, `app/api/favorites/[id]/route.ts`, `app/api/feedback/route.ts`.
**Acceptance criteria:** Each user sees only their own favorites and feedback; cross-user access is denied; new records carry the owner; legacy records handled per the chosen rule; `tsc` passes.
**Risk:** high

## Depends On

task-004
