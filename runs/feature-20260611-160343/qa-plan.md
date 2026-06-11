# QA Plan

## Feature Request

Epic task: Task 019 — Finish Benchmark page remaining English

## Based On Plan

I now have a complete picture. No file modifications needed — here is the plan.

# Implementation Plan

## Summary

Task 019 finishes Russifying the Benchmark page flow and its supporting API routes. The Benchmark page UI (`app/benchmark/page.tsx`) is already fully Russian, but the API routes it (and sibling features) call still return **English error/message strings** that surface to users via `body.error`. The work is a string-only translation pass over the listed API routes — translating human-readable error messages to Russian while leaving machine-readable values (health-probe `status`, backend names) untouched. One visible-English gap remains in `components/BenchmarkTable.tsx` ("Collected"/"Selected") that should be included to truly "finish" the page (see Risks).

## Files To Inspect

- `app/benchmark/page.tsx` — confirmed already fully Russian; no visible English remains. Serves as the style reference (e.g. `"Не удалось запустить бенчмарк."`).
- `app/api/benchmark/route.ts` — English: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
- `app/api/analyze/route.ts` — English: same API-key/JSON strings + `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
- `app/api/auth/login/route.ts` — English: `"Server auth is not configured."`, `"Invalid request."` (note `"Неверный логин или пароль."` already Russian — match this tone).
- `app/api/auth/logout/route.ts` — no user-facing strings; no change.
- `app/api/favorites/route.ts` — English: `"Invalid JSON."`, `"articleId is required."`
- `app/api/favorites/[id]/route.ts` — English: `"Invalid JSON."`, `"Not found."`
- `app/api/feedback/route.ts` — English: `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
- `app/api/jobs/[jobId]/route.ts` — English: `"Job not found"` (error field).
- `app/api/overview/route.ts` — no user-facing strings; no change.
- `app/api/health/route.ts` & `app/api/health/db/route.ts` — only machine-readable values (`status: "ok"`, `"postgres"`, `"local-fs"`, `note: "not using postgres"`); **leave untouched** (consumed by platform health checks).
- `components/BenchmarkTable.tsx` (not in affected list) — visible English row labels `"Collected"` / `"Selected"`. Flag for inclusion.

## Implementation Steps

1. **`app/api/benchmark/route.ts`** — translate the three error messages, e.g. `"Ожидается JSON-тело запроса."`, `"Загруженный файл не найден."`. Keep the `ANTHROPIC_API_KEY` env-var name literal inside a Russian sentence.
2. **`app/api/analyze/route.ts`** — translate all four error strings, reusing the same wording as the benchmark route for the shared messages to stay consistent.
3. **`app/api/auth/login/route.ts`** — translate `"Server auth is not configured."` and `"Invalid request."`; match the register of the already-Russian `"Неверный логин или пароль."`.
4. **`app/api/favorites/route.ts`** & **`app/api/favorites/[id]/route.ts`** — translate `"Invalid JSON."`, `"articleId is required."`, `"Not found."`; keep field name `articleId` literal.
5. **`app/api/feedback/route.ts`** — translate `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`.
6. **`app/api/jobs/[jobId]/route.ts`** — translate the `error: "Job not found"` value (keep `status: "not_found"` literal — it's a machine flag the client checks).
7. **`components/BenchmarkTable.tsx`** (recommended) — translate `"Collected"` → `"Собрано"` and `"Selected"` → `"Отобрано"` to match the surrounding Russian metric labels.
8. Use one consistent Russian phrasing for each repeated English string (`"Expected JSON body."`, `"Upload not found."`) across all routes.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — pure string edits should not affect types; confirms nothing broke.
- Grep the affected files for residual ASCII-letter strings in `error:`/`note:` fields to confirm no user-facing English remains (excluding intentional machine values and the `ANTHROPIC_API_KEY` identifier).
- Manual smoke (optional): trigger the Benchmark flow with a bad upload id / non-JSON body and confirm the surfaced toast text is Russian.
- Verify health endpoints still return literal `"ok"` / backend names unchanged.

## Risks

- **Scope ambiguity on `BenchmarkTable.tsx`**: it is genuinely visible English on the Benchmark page but is *not* in the affected-files list. Leaving it makes the task title only partly true; including it touches an unlisted file. Recommendation: include it (step 7) since the epic is "finish Benchmark page."
- **Translating machine-readable values would break things**: the health probes' `status: "ok"`, backend identifiers, and `status: "not_found"` are consumed programmatically — must stay English. Only translate human-facing `error`/message text.
- **Consistency**: the same English string appears in multiple routes (`analyze` + `benchmark`); divergent translations would look sloppy — use identical Russian wording.
- **Non-UI internal text**: code comments and the `ANTHROPIC_API_KEY` env name should remain English; only the quoted user-facing message changes.
- No tests exist in the repo, so validation leans on typecheck + manual/grep verification rather than an automated suite.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 019 — Finish Benchmark page remaining English

## Planner Input

I now have a complete picture. No file modifications needed — here is the plan.

# Implementation Plan

## Summary

Task 019 finishes Russifying the Benchmark page flow and its supporting API routes. The Benchmark page UI (`app/benchmark/page.tsx`) is already fully Russian, but the API routes it (and sibling features) call still return **English error/message strings** that surface to users via `body.error`. The work is a string-only translation pass over the listed API routes — translating human-readable error messages to Russian while leaving machine-readable values (health-probe `status`, backend names) untouched. One visible-English gap remains in `components/BenchmarkTable.tsx` ("Collected"/"Selected") that should be included to truly "finish" the page (see Risks).

## Files To Inspect

- `app/benchmark/page.tsx` — confirmed already fully Russian; no visible English remains. Serves as the style reference (e.g. `"Не удалось запустить бенчмарк."`).
- `app/api/benchmark/route.ts` — English: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
- `app/api/analyze/route.ts` — English: same API-key/JSON strings + `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
- `app/api/auth/login/route.ts` — English: `"Server auth is not configured."`, `"Invalid request."` (note `"Неверный логин или пароль."` already Russian — match this tone).
- `app/api/auth/logout/route.ts` — no user-facing strings; no change.
- `app/api/favorites/route.ts` — English: `"Invalid JSON."`, `"articleId is required."`
- `app/api/favorites/[id]/route.ts` — English: `"Invalid JSON."`, `"Not found."`
- `app/api/feedback/route.ts` — English: `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
- `app/api/jobs/[jobId]/route.ts` — English: `"Job not found"` (error field).
- `app/api/overview/route.ts` — no user-facing strings; no change.
- `app/api/health/route.ts` & `app/api/health/db/route.ts` — only machine-readable values (`status: "ok"`, `"postgres"`, `"local-fs"`, `note: "not using postgres"`); **leave untouched** (consumed by platform health checks).
- `components/BenchmarkTable.tsx` (not in affected list) — visible English row labels `"Collected"` / `"Selected"`. Flag for inclusion.

## Implementation Steps

1. **`app/api/benchmark/route.ts`** — translate the three error messages, e.g. `"Ожидается JSON-тело запроса."`, `"Загруженный файл не найден."`. Keep the `ANTHROPIC_API_KEY` env-var name literal inside a Russian sentence.
2. **`app/api/analyze/route.ts`** — translate all four error strings, reusing the same wording as the benchmark route for the shared messages to stay consistent.
3. **`app/api/auth/login/route.ts`** — translate `"Server auth is not configured."` and `"Invalid request."`; match the register of the already-Russian `"Неверный логин или пароль."`.
4. **`app/api/favorites/route.ts`** & **`app/api/favorites/[id]/route.ts`** — translate `"Invalid JSON."`, `"articleId is required."`, `"Not found."`; keep field name `articleId` literal.
5. **`app/api/feedback/route.ts`** — translate `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`.
6. **`app/api/jobs/[jobId]/route.ts`** — translate the `error: "Job not found"` value (keep `status: "not_found"` literal — it's a machine flag the client checks).
7. **`components/BenchmarkTable.tsx`** (recommended) — translate `"Collected"` → `"Собрано"` and `"Selected"` → `"Отобрано"` to match the surrounding Russian metric labels.
8. Use one consistent Russian phrasing for each repeated English string (`"Expected JSON body."`, `"Upload not found."`) across all routes.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — pure string edits should not affect types; confirms nothing broke.
- Grep the affected files for residual ASCII-letter strings in `error:`/`note:` fields to confirm no user-facing English remains (excluding intentional machine values and the `ANTHROPIC_API_KEY` identifier).
- Manual smoke (optional): trigger the Benchmark flow with a bad upload id / non-JSON body and confirm the surfaced toast text is Russian.
- Verify health endpoints still return literal `"ok"` / backend names unchanged.

## Risks

- **Scope ambiguity on `BenchmarkTable.tsx`**: it is genuinely visible English on the Benchmark page but is *not* in the affected-files list. Leaving it makes the task title only partly true; including it touches an unlisted file. Recommendation: include it (step 7) since the epic is "finish Benchmark page."
- **Translating machine-readable values would break things**: the health probes' `status: "ok"`, backend identifiers, and `status: "not_found"` are consumed programmatically — must stay English. Only translate human-facing `error`/message text.
- **Consistency**: the same English string appears in multiple routes (`analyze` + `benchmark`); divergent translations would look sloppy — use identical Russian wording.
- **Non-UI internal text**: code comments and the `ANTHROPIC_API_KEY` env name should remain English; only the quoted user-facing message changes.
- No tests exist in the repo, so validation leans on typecheck + manual/grep verification rather than an automated suite.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/benchmark/route.ts
- Other: app/benchmark/page.tsx
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
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

- app/api/benchmark/route.ts
- app/benchmark/page.tsx
- app/api/analyze/route.ts
- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts
- app/api/feedback/route.ts
- app/api/health/db/route.ts
- app/api/health/route.ts
- app/api/jobs/[jobId]/route.ts
- app/api/overview/route.ts

## Required Command

```bash
npx tsc --noEmit
```