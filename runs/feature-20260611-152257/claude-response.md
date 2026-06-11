# Claude Response

The user declined to pick, so I'll proceed with the safest sensible defaults and make every assumption explicit in the plan. No files will be modified — this is plan-only.

## Implementation Plan — Task 019: Finish Benchmark page remaining English

### Goal
Translate the remaining user-facing English strings so the Benchmark page (and the API responses it and sibling pages surface) read fully in Russian — matching the existing translation pattern already applied to `page.tsx`, NavBar, reports, and feedback.

### Guiding assumptions (chosen defaults, since scope questions were declined)
1. **Scope = all user-facing error strings** across the listed API routes (broadest reading of "finish remaining English").
2. **Machine-readable / probe values are left in English** — `health` + `health/db` JSON (`status:"ok"`, `note:"not using postgres"`, `backend`), and machine status enums like `status:"not_found"`. These are consumed by platform health checks and client logic; translating them risks breaking probes/comparisons. Only the human-readable `error` message text is touched.
3. **`components/BenchmarkTable.tsx` IS included** (recommended) — its `"Collected"`/`"Selected"` labels are the most visible English on the rendered page, even though the file is outside the stated affected-files list. This is the one step that goes slightly out of the listed scope; it is isolated and trivially reversible. If strict adherence to affected files is required, this step can be dropped.

### Changes, file by file

**Already complete — no change:**
- `app/benchmark/page.tsx` — fully Russian already.
- `app/api/auth/logout/route.ts` — no user-facing strings.
- `app/api/overview/route.ts` — only JSON data keys, no UI text.
- `app/api/health/route.ts`, `app/api/health/db/route.ts` — only machine/probe values (left English per assumption 2).

**`components/BenchmarkTable.tsx`** (visible page labels):
- L45 `"Collected"` → `"Собрано"`
- L46 `"Selected"` → `"Отобрано"`

**`app/api/benchmark/route.ts`** (errors surface via the page's `setError`):
- L24 `"ANTHROPIC_API_KEY is not set on the server."` → `"ANTHROPIC_API_KEY не задан на сервере."` (keep the env-var name verbatim)
- L39 `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
- L42 `"Upload not found."` → `"Загрузка не найдена."`

**`app/api/analyze/route.ts`:**
- L16 `"ANTHROPIC_API_KEY is not set on the server."` → `"ANTHROPIC_API_KEY не задан на сервере."`
- L36 `"Expected JSON body."` → `"Ожидается тело запроса в формате JSON."`
- L40 `"Missing uploadId."` → `"Отсутствует uploadId."`
- L44 `"Upload not found. Please upload the file again."` → `"Загрузка не найдена. Пожалуйста, загрузите файл ещё раз."`

**`app/api/jobs/[jobId]/route.ts`:**
- L21 `error: "Job not found"` → `"Задача не найдена"` (translate the human message; **keep** `status: "not_found"` and `logs: []` unchanged)

**`app/api/favorites/route.ts`:**
- `"Invalid JSON."` → `"Некорректный JSON."`
- `"articleId is required."` → `"Требуется articleId."`

**`app/api/favorites/[id]/route.ts`:**
- `"Invalid JSON."` → `"Некорректный JSON."`
- `"Not found."` → `"Не найдено."`

**`app/api/feedback/route.ts`:**
- `"Invalid JSON."` → `"Некорректный JSON."`
- `"articleId is required."` → `"Требуется articleId."`
- `"Invalid vote."` → `"Некорректная оценка."`

**`app/api/auth/login/route.ts`** (auth file — flagged; see Risks):
- L31 `"Server auth is not configured."` → `"Аутентификация на сервере не настроена."`
- L39 `"Invalid request."` → `"Некорректный запрос."`
- (L48 `"Неверный логин или пароль."` already Russian — no change)

### What is intentionally NOT changed
- Auth/session **logic**, cookie handling, timing-safe compare — only display strings touched.
- Env-var names, JSON keys, machine status enums, health-probe payloads.
- Comments and JSDoc (developer-facing, not UI). Code-quality strings like `"not using postgres"` stay as-is.

### Risks / uncertainties to confirm
- **Auth rule:** the task rules say "do not modify auth … unless explicitly required." `auth/login/route.ts` is in the affected list (explicitly in scope) and only display strings change, so this is low-risk — but it's the spot most worth a second look. Easy to drop if you'd rather not touch auth at all.
- **BenchmarkTable.tsx is outside the listed affected files.** Included because it's the literal visible English on the page; drop this one step if strict file-scope is required.
- **No string-equality coupling:** error strings are surfaced via `body.error` to the user and not compared programmatically anywhere I saw, so translating them is behavior-safe. Worth a quick grep for any client code that matches on these exact strings before implementing.

### Verification (when later executed)
1. `npm run build` / typecheck — pure string edits, should be clean.
2. Manually exercise the Benchmark page: upload → config → run, confirm table labels and any error toasts render in Russian.
3. Grep the codebase for each old English string to confirm no remaining reference or equality check.

All edits are single-line string swaps — small, isolated, and trivially reversible. Stopping here per plan-only mode.

