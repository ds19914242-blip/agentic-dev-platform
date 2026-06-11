# QA Plan

## Feature Request

Epic task: Task 020 — Translate SourcePicker and PreviewPanel remaining English

## Based On Plan

# Implementation Plan

## Summary

Task 020 finishes the Russian localization sweep for the upload/source-selection flow. Two UI components (`SourcePicker.tsx`, `PreviewPanel.tsx`) still render hardcoded English labels, and the listed API routes return English error strings that surface to users via toasts/error states. The work is pure string translation — replace user-facing English with Russian, preserving all logic, JSX structure, machine-readable API-contract values, code comments, and technical identifiers.

## Files To Inspect

- **components/SourcePicker.tsx** — option labels `"Upload TXT file"`, `"RSS Collection"`.
- **components/PreviewPanel.tsx** — eyebrow `"Preview · No LLM yet"`, `Quality {n}%`, KpiCard labels `Title/Summary/Link/Date`, button `"✨ AI summaries"`, badge `"✨ AI summary"`. (Body prose is already Russian and uses the term "AI-описания" — match it.)
- **app/api/analyze/route.ts** — 4 error strings.
- **app/api/benchmark/route.ts** — 3 error strings (mirror analyze).
- **app/api/auth/login/route.ts** — `"Server auth is not configured."`, `"Invalid request."` (credential message already Russian — use as the tone reference).
- **app/api/feedback/route.ts** — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`.
- **app/api/favorites/route.ts** & **app/api/favorites/[id]/route.ts** — `"Invalid JSON."`, `"articleId is required."`, `"Not found."`.
- **app/api/auth/logout/route.ts** — no user-facing strings; expect no change.
- **app/api/health/route.ts** & **app/api/health/db/route.ts** — only machine-readable diagnostic fields (`status: "ok"`, `storageBackend`, `note: "not using postgres"`). These are API contract / diagnostic values, **not UI text** — leave unchanged.
- **lib/uploadPreview.ts** — DTO builder; only code comments and data-derived labels. Expect no change.

## Implementation Steps

1. **SourcePicker.tsx**: translate the two `label` values (e.g. `"Загрузить TXT-файл"`, `"RSS-коллекция"`). Keep `id` union (`"txt"|"rss"`) and glyphs untouched.
2. **PreviewPanel.tsx**: translate the eyebrow, the `Quality` label, the four KpiCard `label` props, and the AI-summary button/badge text. For the AI strings reuse the existing term "AI-описания" already in the body copy for consistency (e.g. button `"✨ AI-описания"`, badge `"✨ AI-описание"`). Do not touch `className`, interpolated values, or the already-Russian strings/error fallbacks (lines 37, 44).
3. **API error messages**: in analyze, benchmark, login, feedback, favorites routes, translate each human-readable `error` string to Russian, keeping JSON keys, status codes, and field names (e.g. `articleId`) intact. Keep the env-var name `ANTHROPIC_API_KEY` literal inside its message but render the surrounding sentence in Russian.
4. **Leave untouched**: health routes' contract fields, `uploadPreview.ts`, `logout`, all code comments, JSDoc, console output, and storage/backend identifiers.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) — confirm no type/JSX breakage from edits.
- Run the linter/build if configured (`next build` / `next lint`) to ensure no unterminated strings or escaping issues (Russian quotes «», em-dashes).
- Grep the two components for remaining `[A-Za-z]{3,}` in JSX text nodes to confirm no English label slipped through (ignore `className`, prop names, URLs).
- Manual spot check: upload flow renders SourcePicker + PreviewPanel; trigger an error path (bad JSON / missing uploadId) to confirm the toast shows Russian.

## Risks

- **Over-translation**: changing machine-readable API fields (health `status`/`backend`, vote enums, `articleId`) would break clients/middleware. Restrict edits to human-readable `error`/UI strings only.
- **Encoding/escaping**: Cyrillic plus special punctuation in JSX/TS string literals must stay UTF-8 and properly quoted; watch apostrophes in JSX text.
- **Term consistency**: ensure AI-summary wording matches the existing "AI-описания" phrasing already present in PreviewPanel so the UI doesn't mix variants.
- **Scope creep**: health/logout/uploadPreview are listed but likely need no change — confirm rather than inventing translations.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 020 — Translate SourcePicker and PreviewPanel remaining English

## Planner Input

# Implementation Plan

## Summary

Task 020 finishes the Russian localization sweep for the upload/source-selection flow. Two UI components (`SourcePicker.tsx`, `PreviewPanel.tsx`) still render hardcoded English labels, and the listed API routes return English error strings that surface to users via toasts/error states. The work is pure string translation — replace user-facing English with Russian, preserving all logic, JSX structure, machine-readable API-contract values, code comments, and technical identifiers.

## Files To Inspect

- **components/SourcePicker.tsx** — option labels `"Upload TXT file"`, `"RSS Collection"`.
- **components/PreviewPanel.tsx** — eyebrow `"Preview · No LLM yet"`, `Quality {n}%`, KpiCard labels `Title/Summary/Link/Date`, button `"✨ AI summaries"`, badge `"✨ AI summary"`. (Body prose is already Russian and uses the term "AI-описания" — match it.)
- **app/api/analyze/route.ts** — 4 error strings.
- **app/api/benchmark/route.ts** — 3 error strings (mirror analyze).
- **app/api/auth/login/route.ts** — `"Server auth is not configured."`, `"Invalid request."` (credential message already Russian — use as the tone reference).
- **app/api/feedback/route.ts** — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`.
- **app/api/favorites/route.ts** & **app/api/favorites/[id]/route.ts** — `"Invalid JSON."`, `"articleId is required."`, `"Not found."`.
- **app/api/auth/logout/route.ts** — no user-facing strings; expect no change.
- **app/api/health/route.ts** & **app/api/health/db/route.ts** — only machine-readable diagnostic fields (`status: "ok"`, `storageBackend`, `note: "not using postgres"`). These are API contract / diagnostic values, **not UI text** — leave unchanged.
- **lib/uploadPreview.ts** — DTO builder; only code comments and data-derived labels. Expect no change.

## Implementation Steps

1. **SourcePicker.tsx**: translate the two `label` values (e.g. `"Загрузить TXT-файл"`, `"RSS-коллекция"`). Keep `id` union (`"txt"|"rss"`) and glyphs untouched.
2. **PreviewPanel.tsx**: translate the eyebrow, the `Quality` label, the four KpiCard `label` props, and the AI-summary button/badge text. For the AI strings reuse the existing term "AI-описания" already in the body copy for consistency (e.g. button `"✨ AI-описания"`, badge `"✨ AI-описание"`). Do not touch `className`, interpolated values, or the already-Russian strings/error fallbacks (lines 37, 44).
3. **API error messages**: in analyze, benchmark, login, feedback, favorites routes, translate each human-readable `error` string to Russian, keeping JSON keys, status codes, and field names (e.g. `articleId`) intact. Keep the env-var name `ANTHROPIC_API_KEY` literal inside its message but render the surrounding sentence in Russian.
4. **Leave untouched**: health routes' contract fields, `uploadPreview.ts`, `logout`, all code comments, JSDoc, console output, and storage/backend identifiers.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) — confirm no type/JSX breakage from edits.
- Run the linter/build if configured (`next build` / `next lint`) to ensure no unterminated strings or escaping issues (Russian quotes «», em-dashes).
- Grep the two components for remaining `[A-Za-z]{3,}` in JSX text nodes to confirm no English label slipped through (ignore `className`, prop names, URLs).
- Manual spot check: upload flow renders SourcePicker + PreviewPanel; trigger an error path (bad JSON / missing uploadId) to confirm the toast shows Russian.

## Risks

- **Over-translation**: changing machine-readable API fields (health `status`/`backend`, vote enums, `articleId`) would break clients/middleware. Restrict edits to human-readable `error`/UI strings only.
- **Encoding/escaping**: Cyrillic plus special punctuation in JSX/TS string literals must stay UTF-8 and properly quoted; watch apostrophes in JSX text.
- **Term consistency**: ensure AI-summary wording matches the existing "AI-описания" phrasing already present in PreviewPanel so the UI doesn't mix variants.
- **Scope creep**: health/logout/uploadPreview are listed but likely need no change — confirm rather than inventing translations.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- UI component: components/PreviewPanel.tsx
- Library/module: lib/uploadPreview.ts
- UI component: components/SourcePicker.tsx
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts
- API route: app/api/health/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- components/PreviewPanel.tsx
- lib/uploadPreview.ts
- components/SourcePicker.tsx
- app/api/analyze/route.ts
- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/api/benchmark/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts
- app/api/feedback/route.ts
- app/api/health/db/route.ts
- app/api/health/route.ts

## Required Command

```bash
npx tsc --noEmit
```