# Architecture Review

## Feature Request

Change footer text from "Powered by Agentic Dev Platform" to "Работает на Agentic Dev Platform"

## Planner Input

# Implementation Plan

## Summary

Change the footer label rendered in `components/Footer.tsx` from the English `"Powered by Agentic Dev Platform"` to the Russian `"Работает на Agentic Dev Platform"`. This is a single-line static text change.

**Note:** The string lives in `components/Footer.tsx:24` — **not** in any of the "Affected Files" listed in the request (those are API routes and `parseRssTextFile.ts`, none of which contain footer text). A repo-wide grep confirms exactly one occurrence. The listed files appear to be a mismatch and should be ignored for this change.

## Files To Inspect

- `components/Footer.tsx` (line 24) — the only file containing the target string.

## Implementation Steps

1. In `components/Footer.tsx:24`, replace:
   ```tsx
   <span>Powered by Agentic Dev Platform</span>
   ```
   with:
   ```tsx
   <span>Работает на Agentic Dev Platform</span>
   ```
   Keep the product name "Agentic Dev Platform" untranslated (matches the request's target text). No structural/className changes needed.

## Validation Steps

1. Re-grep to confirm no remaining `"Powered by Agentic Dev Platform"` and one new `"Работает на Agentic Dev Platform"`.
2. Ensure the file is saved UTF-8 so Cyrillic renders correctly.
3. `npm run build` (or `tsc`/lint) to confirm no syntax/type errors.
4. Visually verify the footer in any page (footer is shared) shows the new text.

## Risks

- **Low.** Single static-string change with no logic impact.
- **Encoding:** ensure Cyrillic is written as proper UTF-8, not escaped/mojibake.
- **Scope mismatch:** the provided "Affected Files" list is incorrect for this task; editing them would be wrong. The real target is `components/Footer.tsx`.
- **Consistency:** the rest of the footer (e.g. `RSS Agent Lab`, `build`) stays English — confirm partial Russian translation is intended.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Other: src/importers/parseRssTextFile.ts
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
