# Architecture Review

## Feature Request

Epic task: Task 019 — Finish Benchmark page remaining English

## Planner Input

# Implementation Plan

## Summary

The Benchmark **page** (`app/benchmark/page.tsx`) is already fully Russian. The remaining English lives in two places that the Benchmark flow surfaces to the user:

1. **`components/BenchmarkTable.tsx`** — two metric row labels are still English (`"Collected"`, `"Selected"`), and the per-mode status badge renders the raw English job-status enum (`pending/running/done/error`).
2. **API route error strings** that the Benchmark flow (and the listed sibling routes) return via `body.error` — these get shown directly in the UI. The benchmark path uses `/api/upload`, `/api/benchmark`, and `/api/jobs/[jobId]`; the affected-files list extends this to the rest of the API routes for consistency.

Scope = translate user-facing English strings (table labels, status text, API `error`/`note` messages) to Russian. Leave code identifiers, log keys, mode names (`fast/balanced/deep` — already untranslated on the page), and HTTP status semantics untouched.

## Files To Inspect

- `components/BenchmarkTable.tsx` — labels `"Collected"`/`"Selected"` (lines 45–46), status badge `({r.status})` (line 36).
- `app/api/benchmark/route.ts` — errors lines 24, 39, 42; the `[${mode}]` job-name suffix (line 62) is internal, leave it.
- `app/api/jobs/[jobId]/route.ts` — `"Job not found"` (line 20).
- `app/api/analyze/route.ts` — errors lines 16, 36, 40, 44.
- `app/api/auth/login/route.ts` — `"Server auth is not configured."` (30), `"Invalid request."` (39). (Line 47 already Russian.)
- `app/api/favorites/route.ts` — `"Invalid JSON."` (26), `"articleId is required."` (29).
- `app/api/favorites/[id]/route.ts` — `"Invalid JSON."` (16), `"Not found."` (21).
- `app/api/feedback/route.ts` — `"Invalid JSON."` (33), `"articleId is required."` (36), `"Invalid vote."` (39).
- `app/api/health/db/route.ts` — `note: "not using postgres"` (21) — diagnostic, low priority.
- `app/api/auth/logout/route.ts`, `app/api/health/route.ts`, `app/api/overview/route.ts` — no user-facing English strings; no changes needed (status flags like `"ok"` are machine values, keep).

## Implementation Steps

1. **`components/BenchmarkTable.tsx`**
   - Line 45: `"Collected"` → `"Собрано"`.
   - Line 46: `"Selected"` → `"Отобрано"`.
   - (Optional, for completeness) Line 36 status badge: map the enum to Russian via a small lookup, e.g. `{ pending: "ожидание", running: "выполняется", done: "готово", error: "ошибка" }[r.status]`. Keep `r.mode` header (fast/balanced/deep) as-is to match the page's existing untranslated usage.

2. **`app/api/benchmark/route.ts`** — translate the three `error` strings:
   - `"ANTHROPIC_API_KEY is not set on the server."` → e.g. `"ANTHROPIC_API_KEY не задан на сервере."`
   - `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
   - `"Upload not found."` → `"Загруженный файл не найден."`

3. **`app/api/jobs/[jobId]/route.ts`** — `"Job not found"` → `"Задача не найдена"`. Keep `status: "not_found"` (machine value).

4. **`app/api/analyze/route.ts`** — translate the four user-facing errors (ANTHROPIC_API_KEY, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`). Reuse the same Russian wording chosen in step 2 for shared messages.

5. **Auth / favorites / feedback routes** — translate the remaining `error` strings to Russian consistently (`"Invalid JSON." → "Некорректный JSON."`, `"Not found." → "Не найдено."`, `"articleId is required." → "Требуется articleId."`, `"Invalid vote." → "Некорректная оценка."`, `"Server auth is not configured." → "Авторизация на сервере не настроена."`, `"Invalid request." → "Некорректный запрос."`). Keep field names like `articleId` literal where they're identifiers.

6. **`app/api/health/db/route.ts`** (optional) — `note: "not using postgres"` → `"postgres не используется"` if diagnostic notes are in-scope; otherwise skip.

Use one shared phrasing per repeated message so the same English string maps to the same Russian everywhere.

## Validation Steps

- `npx tsc --noEmit` (or the project's typecheck) — confirms no TS breakage from edited string literals.
- Run the app, open `/benchmark`: verify the upload→config→run flow shows the table with `Собрано`/`Отобрано` labels and (if implemented) Russian status badges.
- Trigger an error path to confirm Russian messages surface: e.g. POST `/api/benchmark` with a missing/invalid body, and poll `/api/jobs/<bad-id>`.
- Grep the touched files for residual English UI strings: `Grep` for `[A-Za-z]` inside JSX text and `error: "` literals in the route files.

## Risks

- **Shared strings drift**: the same English message (e.g. "Expected JSON body.", "ANTHROPIC_API_KEY…") appears in multiple routes — translate them identically to avoid inconsistent wording.
- **Translating machine values**: do not change status enums/flags (`"ok"`, `"not_found"`, `"pending"`, backend names), profile/job-name internals (`[${mode}]`), or field identifiers — only human-readable `error`/`note`/label text. Changing enums would break client logic (`view.status === "done"`, the polling stop condition).
- **Status badge mapping is optional**: if added, ensure the lookup covers all four enum values so no status renders blank.
- **Scope ambiguity**: task title names only the Benchmark page, but the affected-files list spans many routes. Plan translates user-facing error text across all listed routes; if the intent is strictly the Benchmark page, limit to steps 1–3.


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
