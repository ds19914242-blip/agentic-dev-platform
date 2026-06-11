# Claude Response

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

