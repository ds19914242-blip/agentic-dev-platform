# Architecture Review

## Feature Request

Epic task: Task 006 — Translate Reading List page

## Planner Input

# Implementation Plan

## Summary

Translate all user-facing English copy on the Reading List page (`app/reading-list/page.tsx`) to Russian, matching the established pattern from prior epic tasks (Dashboard, Hero, NavBar): replace display strings only, leaving all code, logic, props, API endpoints, and `className` values untouched. The listed `app/api/**` routes are part of the affected-files set but serve JSON to the client and contain no end-user UI text; they should be inspected and left unchanged unless a route returns a string surfaced directly in the UI.

## Files To Inspect

- `app/reading-list/page.tsx` — the only file requiring edits; contains all the UI strings.
- `app/dashboard/page.tsx` (commit `51eb9ef`) — reference for translation tone/terminology (e.g. "Избранное", "(без названия)", `toLocaleString("ru-RU")`).
- `app/api/favorites/route.ts` & `app/api/favorites/[id]/route.ts` — confirm responses are JSON only (no user-visible message strings to translate); verify GET/PATCH/DELETE contract used by the page is unchanged.
- The remaining `app/api/**` routes in the affected list — quick scan to confirm no UI-facing strings; expected to need no changes.

## Implementation Steps

1. In `app/reading-list/page.tsx`, translate the header block:
   - `"Reading List"` → `"Список для чтения"`
   - `"Articles you saved for later."` → `"Статьи, сохранённые на потом."`
2. Filter chips (line 55): `"All"` → `"Все"`, `"Unread"` → `"Непрочитанные"`, `"Read"` → `"Прочитанные"`. Keep the filter keys (`"all" | "unread" | "read"`) and `setFilter` logic unchanged.
3. Empty/zero states (lines 63–67):
   - `"Nothing saved yet — use ⭐ Save for Later on report articles."` → `"Пока ничего не сохранено — используйте ⭐ «Сохранить на потом» в статьях отчёта."` (reuse the exact Dashboard wording for consistency).
   - `"Nothing for this filter."` → `"Ничего нет для этого фильтра."`
4. Badges: keep `"Telegram"` as-is; `"Read"` badge (line 81) → `"Прочитано"`.
5. Card content: `"(untitled)"` → `"(без названия)"` (matches Dashboard); in the meta line (line 91) translate `saved` → `сохранено` (`{f.source} · сохранено {…}`); keep the existing `toLocaleDateString("ru-RU")`.
6. Action bar: `"Open Source ↗"` → `"Открыть источник ↗"`; `"Mark unread"` → `"Отметить непрочитанным"` and `"Mark as Read"` → `"Отметить прочитанным"`; `"Remove"` → `"Удалить"`.
7. Toast on removal (line 31): `toast("Removed", "success")` → `toast("Удалено", "success")`. Keep the `"success"` severity key unchanged.
8. Leave all imports, hooks, fetch calls, `className`s, and the `FavoriteArticle` typing untouched.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) to confirm no type/JSX breakage.
- `npm run lint` if configured.
- `npm run build` / `next build` to confirm the page compiles.
- Manual/visual check of `/reading-list`: verify all three filter chips, both empty states (no items vs. filtered-empty), the read/unread badge, action buttons, the remove toast, and the date line render in Russian and still function.
- Confirm favorites API calls (GET/PATCH/DELETE) still work end-to-end after edits.

## Risks

- **Scope creep into API routes:** The affected-files list includes many `app/api/**` routes that have no UI strings. Editing them risks breaking JSON contracts for no benefit — limit changes to `page.tsx`.
- **Filter-key coupling:** The chip labels are derived from the literal union `["all","unread","read"]`. Only the displayed label text (the ternary on line 55) should change; altering the keys would break filtering logic.
- **Terminology consistency:** Use the same Russian terms already chosen in Dashboard ("Избранное", "(без названия)", "Сохранить на потом") to avoid drift across pages.
- **Locale already Russian:** Date formatting already uses `"ru-RU"`; no change needed there — avoid redundant edits.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Other: app/reading-list/page.tsx
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts
- API route: app/api/health/route.ts
- API route: app/api/jobs/[jobId]/route.ts
- API route: app/api/overview/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
