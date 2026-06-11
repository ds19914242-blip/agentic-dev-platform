# Approved Plan

No answers came back, so I'll proceed with the recommended defaults and present the plan, clearly marking those assumptions so you can adjust.

---

# Implementation Plan — Task 019: Finish Benchmark page remaining English

## Goal
Eliminate the remaining English text that can appear to a Russian-speaking user in the Benchmark page flow and the user-facing API error responses, matching the existing translation precedent (e.g. `auth/login` already returns `"Неверный логин или пароль."`).

## Assumptions (from the unanswered scope questions — adjust if wrong)
- **A1:** Include `components/BenchmarkTable.tsx` — it holds the only visible English actually rendered on the Benchmark page.
- **A2:** Translate user-facing error strings across analyze, benchmark, jobs, favorites, feedback.
- **A3:** Leave `auth/login`, `health`, `health/db`, and `overview` untouched (auth is protected by the rules; the rest are machine/ops diagnostics, not UI).

## Scope: exact edits

### 1. `components/BenchmarkTable.tsx` (visible UI text)
- Line 45: `["Collected", …]` → `["Собрано", …]`
- Line 46: `["Selected", …]` → `["Отобрано", …]`
- No logic change — these are display labels in the metrics-row array. All sibling labels (`"Время"`, `"Из кэша"`, etc.) are already Russian.

### 2. `app/api/benchmark/route.ts` (errors surfaced by the Benchmark page)
- L24: `"ANTHROPIC_API_KEY is not set on the server."` → `"Ключ ANTHROPIC_API_KEY не задан на сервере."`
- L39: `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
- L42: `"Upload not found."` → `"Загруженный файл не найден."`

### 3. `app/api/analyze/route.ts`
- L16: `"ANTHROPIC_API_KEY is not set on the server."` → same as above
- L36: `"Expected JSON body."` → same as above
- L40: `"Missing uploadId."` → `"Не указан идентификатор загрузки."`
- L44: `"Upload not found. Please upload the file again."` → `"Загруженный файл не найден. Пожалуйста, загрузите файл заново."`

### 4. `app/api/jobs/[jobId]/route.ts`
- L20: `error: "Job not found"` → `"Задача не найдена"`
  - Note: the Benchmark page only reads `view.status`, so this surfaces on *other* pages, not the benchmark flow. Included for consistency under A2. The `status: "not_found"` value is a machine field and stays as-is.

### 5. `app/api/favorites/route.ts`
- L26: `"Invalid JSON."` → `"Некорректный JSON."`
- L29: `"articleId is required."` → `"Не указан articleId."`

### 6. `app/api/favorites/[id]/route.ts`
- L16: `"Invalid JSON."` → `"Некорректный JSON."`
- L21: `"Not found."` → `"Не найдено."`

### 7. `app/api/feedback/route.ts`
- L33: `"Invalid JSON."` → `"Некорректный JSON."`
- L36: `"articleId is required."` → `"Не указан articleId."`
- L39: `"Invalid vote."` → `"Некорректный голос."`

## Files intentionally NOT changed (with reason)
- **`app/benchmark/page.tsx`** — already fully Russian; no edits needed (kept in scope only for verification).
- **`app/api/auth/login/route.ts`, `app/api/auth/logout/route.ts`** — auth is protected by the task rules ("do not modify auth … unless explicitly required"); logout has no English UI strings anyway. *(Flip A2/auth if you want `"Server auth is not configured."` / `"Invalid request."` translated.)*
- **`app/api/health/route.ts`, `app/api/health/db/route.ts`** — liveness/diagnostic probes; `status`, `note`, and DB-error passthrough are ops/machine-facing, not user UI.
- **`app/api/overview/route.ts`** — contains no English strings; pure data response.

## What stays in English everywhere (intentional)
- HTTP status values, JSON field names/keys (`status`, `note`, `backend`, `articleId` as a key), code comments, env-var names, and machine-readable enum values like `"not_found"` / `"pending"`. Only human-readable `error` *message values* and visible labels are translated.

## Verification
1. `npx tsc --noEmit` (or the project's typecheck) — edits are string-literal-only, so types are unaffected; this just confirms no accidental syntax breakage.
2. Manual/`/run`: open `/benchmark`, run a benchmark, confirm the table shows `Собрано` / `Отобрано`; trigger an error path (e.g. malformed request) to confirm Russian error text appears.
3. `git diff` review — confirm only string values changed, no logic touched.

## Risk & reversibility
- Changes are isolated string-literal replacements across 7 files — low risk, trivially reversible via `git revert`.
- No auth, billing, secrets, schema, or deploy config touched.

This is plan only — no files have been modified. Let me know if you want to change any of the three scope assumptions (BenchmarkTable inclusion, error-scope breadth, auth/ops handling) and I'll adjust before any implementation.

