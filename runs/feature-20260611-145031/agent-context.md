# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 004 — Translate Dashboard page

## Planner Input

I now have enough context to produce the plan. The Dashboard page is fully English; the report-rendering `Dashboard.tsx`/`StatsPanel.tsx` are partly translated already; API routes carry user-facing JSON error strings (one, login, is already Russian).

# Implementation Plan

## Summary

Translate all user-facing text on the Dashboard page to Russian, matching the established pattern from Tasks 001/003 (NavBar, Hero) and the already-Russian report components. The primary surface is `app/dashboard/page.tsx` (currently 100% English). Secondary cleanup: finish translating the leftover English strings in `components/Dashboard.tsx` and `components/StatsPanel.tsx`, and translate the user-facing error messages returned by the listed API routes for consistency. No logic, data shapes, or `href`/locale formatting (`ru-RU`) changes.

## Files To Inspect

- `app/dashboard/page.tsx` — main target; eyebrow, headings, quick-action labels, overview card labels, section headers, empty states, button labels.
- `components/Dashboard.tsx` — leftover English: "Intelligence Report", "Collected/Selected/Potentially Relevant/Trends/Generated", "Potentially Relevant" heading + description, four `ChartCard` titles.
- `components/StatsPanel.tsx` — section headings "Processing" / "Performance" (rows already Russian).
- `lib/dashboard.ts` — types only; confirm no user-facing strings (none expected — type definitions).
- API routes (`app/api/overview`, `analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`) — inspect each for `error`/message strings returned to the client; translate user-facing ones (login already Russian, use as tone reference).

## Implementation Steps

1. **`app/dashboard/page.tsx`** — translate:
   - Eyebrow `Workspace` → e.g. `Рабочее пространство`; `h1` "Your intelligence dashboard" (keep gradient `<span>` split, translate both parts).
   - Quick actions: `Run Analysis`, `Add Source`, `Create Collection`.
   - Overview: `Overview`, card labels `Sources`/`Collections`/`Reports`/`Favorites`.
   - Latest Reports: `Latest Reports`, `View all →`, empty state "No reports yet. Run your first analysis →", inline `selected`/`trends` words in the meta line, `Open`, `Export`.
   - Recent Saved / Recent Activity: headings, empty states ("Nothing saved yet — use ⭐ Save for Later…", "No analysis runs yet."), `(untitled)` fallback.
   - Leave `href`, icon glyphs, and `toLocaleString("ru-RU")` untouched.
2. **`components/Dashboard.tsx`** — translate the remaining English: header eyebrow/meta line labels, "Generated:", "Potentially Relevant" heading + paragraph, and the four `ChartCard` titles. Keep already-Russian strings as-is.
3. **`components/StatsPanel.tsx`** — translate the two section headings `Processing` / `Performance`.
4. **API routes** — translate user-facing `NextResponse.json({ error: ... })` messages to Russian (e.g. `analyze`: "Upload not found…", "Missing uploadId."; `feedback`: "Invalid vote." etc.). Keep server-config/developer errors (e.g. "ANTHROPIC_API_KEY is not set") per the project's existing convention — match whatever the login route's precedent implies (it translated the user-credential error but these are dev errors). Confirm convention before mass-translating; if uncertain, limit API changes to clearly end-user-visible validation messages.
5. Ensure no JSX structure, className, or key changes; only text node / string-literal content.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- `npm run build` / `next build` to confirm pages compile.
- Manual: run dev server, load `/dashboard`, verify all visible strings are Russian and layout/gradient text intact; trigger an empty state if feasible.
- Grep `app/dashboard/page.tsx` for residual English words to confirm full coverage.

## Risks


## plan

I now have enough context to produce the plan. The Dashboard page is fully English; the report-rendering `Dashboard.tsx`/`StatsPanel.tsx` are partly translated already; API routes carry user-facing JSON error strings (one, login, is already Russian).

# Implementation Plan

## Summary

Translate all user-facing text on the Dashboard page to Russian, matching the established pattern from Tasks 001/003 (NavBar, Hero) and the already-Russian report components. The primary surface is `app/dashboard/page.tsx` (currently 100% English). Secondary cleanup: finish translating the leftover English strings in `components/Dashboard.tsx` and `components/StatsPanel.tsx`, and translate the user-facing error messages returned by the listed API routes for consistency. No logic, data shapes, or `href`/locale formatting (`ru-RU`) changes.

## Files To Inspect

- `app/dashboard/page.tsx` — main target; eyebrow, headings, quick-action labels, overview card labels, section headers, empty states, button labels.
- `components/Dashboard.tsx` — leftover English: "Intelligence Report", "Collected/Selected/Potentially Relevant/Trends/Generated", "Potentially Relevant" heading + description, four `ChartCard` titles.
- `components/StatsPanel.tsx` — section headings "Processing" / "Performance" (rows already Russian).
- `lib/dashboard.ts` — types only; confirm no user-facing strings (none expected — type definitions).
- API routes (`app/api/overview`, `analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`) — inspect each for `error`/message strings returned to the client; translate user-facing ones (login already Russian, use as tone reference).

## Implementation Steps

1. **`app/dashboard/page.tsx`** — translate:
   - Eyebrow `Workspace` → e.g. `Рабочее пространство`; `h1` "Your intelligence dashboard" (keep gradient `<span>` split, translate both parts).
   - Quick actions: `Run Analysis`, `Add Source`, `Create Collection`.
   - Overview: `Overview`, card labels `Sources`/`Collections`/`Reports`/`Favorites`.
   - Latest Reports: `Latest Reports`, `View all →`, empty state "No reports yet. Run your first analysis →", inline `selected`/`trends` words in the meta line, `Open`, `Export`.
   - Recent Saved / Recent Activity: headings, empty states ("Nothing saved yet — use ⭐ Save for Later…", "No analysis runs yet."), `(untitled)` fallback.
   - Leave `href`, icon glyphs, and `toLocaleString("ru-RU")` untouched.
2. **`components/Dashboard.tsx`** — translate the remaining English: header eyebrow/meta line labels, "Generated:", "Potentially Relevant" heading + paragraph, and the four `ChartCard` titles. Keep already-Russian strings as-is.
3. **`components/StatsPanel.tsx`** — translate the two section headings `Processing` / `Performance`.
4. **API routes** — translate user-facing `NextResponse.json({ error: ... })` messages to Russian (e.g. `analyze`: "Upload not found…", "Missing uploadId."; `feedback`: "Invalid vote." etc.). Keep server-config/developer errors (e.g. "ANTHROPIC_API_KEY is not set") per the project's existing convention — match whatever the login route's precedent implies (it translated the user-credential error but these are dev errors). Confirm convention before mass-translating; if uncertain, limit API changes to clearly end-user-visible validation messages.
5. Ensure no JSX structure, className, or key changes; only text node / string-literal content.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- `npm run build` / `next build` to confirm pages compile.
- Manual: run dev server, load `/dashboard`, verify all visible strings are Russian and layout/gradient text intact; trigger an empty state if feasible.
- Grep `app/dashboard/page.tsx` for residual English words to confirm full coverage.

## Risks

- **Scope ambiguity**: the affected-files list pulls in many API routes whose error strings are largely deve

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 004 — Translate Dashboard page

## Based On Plan

I now have enough context to produce the plan. The Dashboard page is fully English; the report-rendering `Dashboard.tsx`/`StatsPanel.tsx` are partly translated already; API routes carry user-facing JSON error strings (one, login, is already Russian).

# Implementation Plan

## Summary

Translate all user-facing text on the Dashboard page to Russian, matching the established pattern from Tasks 001/003 (NavBar, Hero) and the already-Russian report components. The primary surface is `app/dashboard/page.tsx` (currently 100% English). Secondary cleanup: finish translating the leftover English strings in `components/Dashboard.tsx` and `components/StatsPanel.tsx`, and translate the user-facing error messages returned by the listed API routes for consistency. No logic, data shapes, or `href`/locale formatting (`ru-RU`) changes.

## Files To Inspect

- `app/dashboard/page.tsx` — main target; eyebrow, headings, quick-action labels, overview card labels, section headers, empty states, button labels.
- `components/Dashboard.tsx` — leftover English: "Intelligence Report", "Collected/Selected/Potentially Relevant/Trends/Generated", "Potentially Relevant" heading + description, four `ChartCard` titles.
- `components/StatsPanel.tsx` — section headings "Processing" / "Performance" (rows already Russian).
- `lib/dashboard.ts` — types only; confirm no user-facing strings (none expected — type definitions).
- API routes (`app/api/overview`, `analyze`, `auth/login`, `auth/logout`, `benchmark`, `favorites`, `favorites/[id]`, `feedback`) — inspect each for `error`/message strings returned to the client; translate user-facing ones (login already Russian, use as tone reference).

## Implementation Steps

1. **`app/dashboard/page.tsx`** — translate:
   - Eyebrow `Workspace` → e.g. `Рабочее пространство`; `h1` "Your intelligence dashboard" (keep gradient `<span>` split, translate both parts).
   - Quick actions: `Run Analysis`, `Add Source`, `Create Collection`.
   - Overview: `Overview`, card labels `Sources`/`Collections`/`Reports`/`Favorites`.
   - Latest Reports: `Latest Reports`, `View all →`, empty state "No reports yet. Run your first analysis →", inline `selected`/`trends` words in the meta line, `Open`, `Export`.
   - Recent Saved / Recent Activity: headings, empty states ("Nothing saved yet — use ⭐ Save for Later…", "No analysis runs yet."), `(untitled)` fallback.
   - Leave `href`, icon glyphs, and `toLocaleString("ru-RU")` untouched.
2. **`components/Dashboard.tsx`** — translate the remaining English: header eyebrow/meta line labels, "Generated:", "Potentially Relevant" heading + paragraph, and the four `ChartCard` titles. Keep already-Russian strings as-is.
3. **`components/StatsPanel.tsx`** — translate the two section headings `Processing` / `Performance`.
4. **API routes** — translate user-facing `NextResponse.json({ error: ... })` messages to Russian (e.g. `analyze`: "Upload not found…", "Missing uploadId."; `feedback`: "Invalid vote." etc.). Keep server-config/developer errors (e.g. "ANTHROPIC_API_KEY is not set") per the project's existing convention — match whatever the login route's precedent implies (it translated the user-credential error but these are dev errors). Confirm convention before mass-translating; if uncertain, limit API changes to clearly end-user-visible validation messages.
5. Ensure no JSX structure, className, or key changes; only text node / string-literal content.

## Validation Steps

- `npx tsc --noEmit` (or project's typecheck script) — confirm no type errors introduced.
- `npm run lint` if configured.
- `npm run build` / `next build` to confirm pages compile.
- Manual: run dev server, load `/dashboard`, verify all visible strings are Russian and layout/gradient text intact; trigger an empty state if feasible.
- Grep `app/dashboard/page.tsx` for residual English words to confirm full coverage.

## Risks

- **Scope a
