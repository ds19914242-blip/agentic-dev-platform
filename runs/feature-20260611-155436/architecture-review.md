# Architecture Review

## Feature Request

Epic task: Task 012 — Translate StatsPanel remaining English

## Planner Input

The component is clear. The "remaining English" in StatsPanel is just two section headings — all the `Row` labels are already translated. The affected-files list (API routes) is noise; the actual UI text lives in `components/StatsPanel.tsx`.

# Implementation Plan

## Summary

`components/StatsPanel.tsx` has been mostly translated to Russian already — every `Row` label is in Russian. Two visible English strings remain: the section headings **"Processing"** (line 22) and **"Performance"** (line 35). The task is to translate these two remaining headings to Russian, matching the established "translate only visible UI text" pattern used in prior commits.

## Files To Inspect

- `components/StatsPanel.tsx` — confirmed: the only English left is the two `<h2 className="label">` headings. No API-route changes are needed despite the affected-files list.

## Implementation Steps

1. In `components/StatsPanel.tsx` line 22, change `<h2 className="label mb-3">Processing</h2>` → `Обработка` (e.g. "Обработка").
2. In `components/StatsPanel.tsx` line 35, change `<h2 className="label mb-3">Performance</h2>` → `Производительность`.
3. Leave all code, props, types, and class names untouched — change only the two display strings.

Suggested translations (consistent with existing Russian labels in the file):
- `Processing` → `Обработка`
- `Performance` → `Производительность`

## Validation Steps

- Visually scan the file to confirm no English UI strings remain (CSS class names like `label`, `card`, `stat-number` are not user-facing and stay as-is).
- Run `npm run build` / `tsc` to confirm no type or JSX breakage (text-only change should be safe).
- Optionally render a report view to confirm the two headings now display in Russian above their respective stat rows.

## Risks

- **Very low.** Pure visible-text change in one component; no logic, props, or types affected.
- Only ambiguity is word choice for the translations — "Обработка" / "Производительность" align with the existing Russian labels and are recommended; adjust if a project glossary specifies different terms.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

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
- API route: app/api/profiles/[id]/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
