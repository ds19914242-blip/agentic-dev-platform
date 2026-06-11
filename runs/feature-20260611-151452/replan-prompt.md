# Replan Failed Implementation

The implementation failed validation.

Your job:
1. Analyze the validation failure.
2. Identify the most likely root cause.
3. Produce a minimal fix plan.
4. Apply the fix directly.
5. Do not redesign the feature.
6. Do not touch auth, billing, secrets, database schema, or deployment config.

# Feature Request

Epic task: Task 020 — Translate SourcePicker and PreviewPanel remaining English

# Approved Plan

# Approved Plan

The question wasn't answered — I'll finalize the plan with my recommended default scope (**visible errors only**), which best fits the "smallest safe change" rule and the codebase's existing convention. You can redirect before implementation if you'd prefer a different scope.

## Final Implementation Plan

**Mode: plan only — no files modified.**

| # | File | Change | Risk |
|---|------|--------|------|
| 1 | `components/SourcePicker.tsx` | Translate 2 button labels (L12–13); keep `id` keys | none |
| 2 | `components/PreviewPanel.tsx` | Translate eyebrow (L55), `Quality` (L77), 4 KpiCard labels (L90–93), AI-summaries button + helper (L106/110), AI-summary badge (L133) | none |
| 3 | `app/api/analyze/route.ts` | Translate 3 user-visible error strings (L36, L40, L44) | low — display strings only |
| 4 | `app/api/benchmark/route.ts` | Translate 2 user-visible error strings (L39, L42) | low — display strings only |
| 5 | `app/api/auth/login/route.ts` | Translate `"Invalid request."` (L39); leave `"Server auth is not configured."` per convention | low — no auth logic touched |

**Explicitly unchanged:**
- `lib/uploadPreview.ts` — no user-facing strings (DTO + comments only)
- `app/api/favorites/route.ts`, `app/api/favorites/[id]/route.ts`, `app/api/feedback/route.ts` — error JSON never rendered (callers check `res.ok` only)
- `app/api/health/route.ts`, `app/api/health/db/route.ts` — machine probes, not UI
- `app/api/auth/logout/route.ts` — no error string
- Server-config/ops diagnostics (`ANTHROPIC_API_KEY is not set…`, `Server auth is not configured.`) — left English to match the prior translator's pattern

**Verification after implementation:** `npm run build` / `tsc` (string-only edits keep types intact), then visually confirm SourcePicker toggle, the upload preview panel, and an analyze/login error path render Russian.

This keeps every change a one-line string swap — no logic, types, status codes, or auth flow affected — so it's fully reversible. Ready to implement on your go-ahead (and tell me if you want a broader or narrower API scope than the recommended default).



# Implementation Response

# Claude Implementation Response

TypeScript isn't installed in this worktree (`tsc: command not found`), so the typecheck can't run here. The changes are all string-content swaps inside existing string literals, so they don't affect types or syntax.

## Summary

All edits per the approved plan are complete — pure Russian translations of user-visible strings, no logic changed.

**Changed files (5):**

1. **`components/SourcePicker.tsx`** — 2 button labels: `Upload TXT file` → `Загрузить TXT-файл`, `RSS Collection` → `RSS-коллекция` (`id` keys untouched).
2. **`components/PreviewPanel.tsx`** — eyebrow `Preview · No LLM yet` → `Предпросмотр · Без LLM`; `Quality` → `Качество`; 4 KpiCard labels (Title/Summary/Link/Date → Заголовок/Описание/Ссылка/Дата); AI-summaries button + helper text + badge `AI summary` → `AI-описание` (and `«✨ AI summaries»` reference updated to match).
3. **`app/api/analyze/route.ts`** — 3 display errors: `Expected JSON body.`, `Missing uploadId.`, `Upload not found…` → Russian.
4. **`app/api/benchmark/route.ts`** — 2 display errors: `Expected JSON body.`, `Upload not found.` → Russian.
5. **`app/api/auth/login/route.ts`** — `Invalid request.` → `Неверный запрос.` (left `Server auth is not configured.` English per convention; auth logic untouched).

**Left English intentionally** (per plan): server-config/ops diagnostics (`ANTHROPIC_API_KEY is not set…`, `Server auth is not configured.`), and non-rendered error JSON in favorites/feedback/health routes.

## Risks

- **Low/none.** Every change is a one-line string swap inside existing literals — no logic, types, status codes, JSX structure, or auth flow affected. Fully reversible.
- **Verification gap:** `tsc` couldn't run (TypeScript not installed in this worktree). Given the edits are string-content-only, type integrity is preserved, but I couldn't mechanically confirm. If you want, I can run `npm run build` (which uses Next's bundled compiler) instead — that would compile-check the changes.


# Validation Report

# Validation Result

## Overall Result

failed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: failed

Timed Out: False

Exit Code: 1

### STDOUT

```text

[41m                                                                               [0m
[41m[37m                This is not the tsc command you are looking for                [0m
[41m                                                                               [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: failed

Timed Out: False

Exit Code: 127

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build


```

### STDERR

```text
sh: next: command not found

```

