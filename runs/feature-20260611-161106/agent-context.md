# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 019 — Finish Benchmark page remaining English

## Planner Input

I now have a complete picture. Here's the plan.

# Implementation Plan

## Summary

Task 019 finishes the Russian localization of the Benchmark page and the API routes that feed it (or whose errors surface in the UI). The Benchmark page UI (`app/benchmark/page.tsx`) is already fully translated; the remaining English lives in **`components/BenchmarkTable.tsx`** (two row labels + status text) and in the **JSON `error` messages returned by the listed API routes**, which bubble up into user-facing toasts/alerts. The work is string-only: translate user-facing text, leave technical identifiers, JSDoc comments, console logs, HTTP/storage enum values, and mode names untouched.

## Files To Inspect

- `components/BenchmarkTable.tsx` — `"Collected"`, `"Selected"` labels (lines 45–46) and the `({r.status})` text (line 35). Already done: all other row labels are Russian.
- `app/api/benchmark/route.ts` — error strings: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
- `app/api/analyze/route.ts` — `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
- `app/api/jobs/[jobId]/route.ts` — `"Job not found"` (note: `status: "not_found"` is a technical enum — keep).
- `app/api/auth/login/route.ts` — `"Server auth is not configured."`, `"Invalid request."` (the credentials error is already Russian).
- `app/api/favorites/route.ts` & `app/api/favorites/[id]/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
- `app/api/feedback/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
- `app/api/auth/logout/route.ts` — no user-facing strings (no change).
- `app/api/overview/route.ts` — pure JSON data, no user-facing strings (no change).
- `app/api/health/route.ts` & `app/api/health/db/route.ts` — `status: "ok"`, `note: "not using postgres"`, backend enums are diagnostic/machine values, not UI copy → **leave as-is** (confirm during review; these probes aren't shown to end users).

## Implementation Steps

1. **`components/BenchmarkTable.tsx`**: translate the two metric labels — `"Collected"` → `"Собрано"`, `"Selected"` → `"Отобрано"` (matching the existing Russian labels like `"По критериям"`, `"Из кэша"`). Optionally map the inline status badge `({r.status})` (pending/running/done/error) to Russian equivalents (`ожидание/выполняется/готово/ошибка`) for consistency. **Keep** the mode column headers (`fast`/`balanced`/`deep`) — they match the page's intentional "Fast / Balanced / Deep" branding.
2. **API error strings**: translate each user-facing `error` value in the routes above to Russian, e.g.:
   - `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
   - `"Upload not found."` / `"Upload not found. Please upload the file again."` → `"Файл не найден. Загрузите файл заново."`
   - `"Missing uploadId."` → `"Отсутствует uploadId."`
   - `"ANTHROPIC_API_KEY is not set on the server."` → `"ANTHROPIC_API_KEY не задан на сервере."`
   - `"Invalid JSON."` → `"Некорректный JSON."`, `"articleId is required."` → `"Требуется articleId."`, `"Invalid vote."` → `"Некорректная оценка."`, `"Not found."` → `"Не найдено."`, `"Server auth is not configured."` → `"Аутентификация не настроена на сервере."`, `"Invalid request."` → `"Некорректный запрос."`, `"Job not found"` → `"Задача не найдена."`
3. **Do not touch**: JSDoc/inline comments, console/log output, type literals, status/backend enum values (`"ok"`, `"not_found"`, `"postgres"`, etc.), and field keys — only string *values* shown to users.

## Validation Steps

- `npm run build` (or `tsc --noEmit` / lint) to confirm no type/syntax breakage from the string edits.
- Grep the affected files for residual ASCII letters in quoted strings to confirm no user-facing English remains: search for likely 

## plan

I now have a complete picture. Here's the plan.

# Implementation Plan

## Summary

Task 019 finishes the Russian localization of the Benchmark page and the API routes that feed it (or whose errors surface in the UI). The Benchmark page UI (`app/benchmark/page.tsx`) is already fully translated; the remaining English lives in **`components/BenchmarkTable.tsx`** (two row labels + status text) and in the **JSON `error` messages returned by the listed API routes**, which bubble up into user-facing toasts/alerts. The work is string-only: translate user-facing text, leave technical identifiers, JSDoc comments, console logs, HTTP/storage enum values, and mode names untouched.

## Files To Inspect

- `components/BenchmarkTable.tsx` — `"Collected"`, `"Selected"` labels (lines 45–46) and the `({r.status})` text (line 35). Already done: all other row labels are Russian.
- `app/api/benchmark/route.ts` — error strings: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
- `app/api/analyze/route.ts` — `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
- `app/api/jobs/[jobId]/route.ts` — `"Job not found"` (note: `status: "not_found"` is a technical enum — keep).
- `app/api/auth/login/route.ts` — `"Server auth is not configured."`, `"Invalid request."` (the credentials error is already Russian).
- `app/api/favorites/route.ts` & `app/api/favorites/[id]/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
- `app/api/feedback/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
- `app/api/auth/logout/route.ts` — no user-facing strings (no change).
- `app/api/overview/route.ts` — pure JSON data, no user-facing strings (no change).
- `app/api/health/route.ts` & `app/api/health/db/route.ts` — `status: "ok"`, `note: "not using postgres"`, backend enums are diagnostic/machine values, not UI copy → **leave as-is** (confirm during review; these probes aren't shown to end users).

## Implementation Steps

1. **`components/BenchmarkTable.tsx`**: translate the two metric labels — `"Collected"` → `"Собрано"`, `"Selected"` → `"Отобрано"` (matching the existing Russian labels like `"По критериям"`, `"Из кэша"`). Optionally map the inline status badge `({r.status})` (pending/running/done/error) to Russian equivalents (`ожидание/выполняется/готово/ошибка`) for consistency. **Keep** the mode column headers (`fast`/`balanced`/`deep`) — they match the page's intentional "Fast / Balanced / Deep" branding.
2. **API error strings**: translate each user-facing `error` value in the routes above to Russian, e.g.:
   - `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
   - `"Upload not found."` / `"Upload not found. Please upload the file again."` → `"Файл не найден. Загрузите файл заново."`
   - `"Missing uploadId."` → `"Отсутствует uploadId."`
   - `"ANTHROPIC_API_KEY is not set on the server."` → `"ANTHROPIC_API_KEY не задан на сервере."`
   - `"Invalid JSON."` → `"Некорректный JSON."`, `"articleId is required."` → `"Требуется articleId."`, `"Invalid vote."` → `"Некорректная оценка."`, `"Not found."` → `"Не найдено."`, `"Server auth is not configured."` → `"Аутентификация не настроена на сервере."`, `"Invalid request."` → `"Некорректный запрос."`, `"Job not found"` → `"Задача не найдена."`
3. **Do not touch**: JSDoc/inline comments, console/log output, type literals, status/backend enum values (`"ok"`, `"not_found"`, `"postgres"`, etc.), and field keys — only string *values* shown to users.

## Validation Steps

- `npm run build` (or `tsc --noEmit` / lint) to confirm no type/syntax breakage from the string edits.
- Grep the affected files for residual ASCII letters in quoted strings to confirm no user-facing English remains: search for likely leftovers (e.g. `error: "[A-Za-z]`) across the listed routes.
- Manual smoke of the Benchmark page: upload → config → run, c

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 019 — Finish Benchmark page remaining English

## Based On Plan

I now have a complete picture. Here's the plan.

# Implementation Plan

## Summary

Task 019 finishes the Russian localization of the Benchmark page and the API routes that feed it (or whose errors surface in the UI). The Benchmark page UI (`app/benchmark/page.tsx`) is already fully translated; the remaining English lives in **`components/BenchmarkTable.tsx`** (two row labels + status text) and in the **JSON `error` messages returned by the listed API routes**, which bubble up into user-facing toasts/alerts. The work is string-only: translate user-facing text, leave technical identifiers, JSDoc comments, console logs, HTTP/storage enum values, and mode names untouched.

## Files To Inspect

- `components/BenchmarkTable.tsx` — `"Collected"`, `"Selected"` labels (lines 45–46) and the `({r.status})` text (line 35). Already done: all other row labels are Russian.
- `app/api/benchmark/route.ts` — error strings: `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Upload not found."`
- `app/api/analyze/route.ts` — `"ANTHROPIC_API_KEY is not set on the server."`, `"Expected JSON body."`, `"Missing uploadId."`, `"Upload not found. Please upload the file again."`
- `app/api/jobs/[jobId]/route.ts` — `"Job not found"` (note: `status: "not_found"` is a technical enum — keep).
- `app/api/auth/login/route.ts` — `"Server auth is not configured."`, `"Invalid request."` (the credentials error is already Russian).
- `app/api/favorites/route.ts` & `app/api/favorites/[id]/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Not found."`
- `app/api/feedback/route.ts` — `"Invalid JSON."`, `"articleId is required."`, `"Invalid vote."`
- `app/api/auth/logout/route.ts` — no user-facing strings (no change).
- `app/api/overview/route.ts` — pure JSON data, no user-facing strings (no change).
- `app/api/health/route.ts` & `app/api/health/db/route.ts` — `status: "ok"`, `note: "not using postgres"`, backend enums are diagnostic/machine values, not UI copy → **leave as-is** (confirm during review; these probes aren't shown to end users).

## Implementation Steps

1. **`components/BenchmarkTable.tsx`**: translate the two metric labels — `"Collected"` → `"Собрано"`, `"Selected"` → `"Отобрано"` (matching the existing Russian labels like `"По критериям"`, `"Из кэша"`). Optionally map the inline status badge `({r.status})` (pending/running/done/error) to Russian equivalents (`ожидание/выполняется/готово/ошибка`) for consistency. **Keep** the mode column headers (`fast`/`balanced`/`deep`) — they match the page's intentional "Fast / Balanced / Deep" branding.
2. **API error strings**: translate each user-facing `error` value in the routes above to Russian, e.g.:
   - `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
   - `"Upload not found."` / `"Upload not found. Please upload the file again."` → `"Файл не найден. Загрузите файл заново."`
   - `"Missing uploadId."` → `"Отсутствует uploadId."`
   - `"ANTHROPIC_API_KEY is not set on the server."` → `"ANTHROPIC_API_KEY не задан на сервере."`
   - `"Invalid JSON."` → `"Некорректный JSON."`, `"articleId is required."` → `"Требуется articleId."`, `"Invalid vote."` → `"Некорректная оценка."`, `"Not found."` → `"Не найдено."`, `"Server auth is not configured."` → `"Аутентификация не настроена на сервере."`, `"Invalid request."` → `"Некорректный запрос."`, `"Job not found"` → `"Задача не найдена."`
3. **Do not touch**: JSDoc/inline comments, console/log output, type literals, status/backend enum values (`"ok"`, `"not_found"`, `"postgres"`, etc.), and field keys — only string *values* shown to users.

## Validation Steps

- `npm run build` (or `tsc --noEmit` / lint) to confirm no type/syntax breakage from the string edits.
- Grep the affected files for residual ASCII letters in quoted strings to confirm no user-facing English remains: search for likely leftovers (e
