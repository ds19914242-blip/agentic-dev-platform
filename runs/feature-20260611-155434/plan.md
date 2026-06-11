# Implementation Plan

## Summary

Translate the remaining English-language strings in the analysis progress UI/output to Russian, matching the already-Russian surrounding copy (e.g. `Подготовка…`, `Прошло`, `Готово`). Two concrete English strings remain user-visible in the progress flow, plus the CLI progress reporter (`src/util/progress.ts`) is still entirely in English. The listed `app/api/**/route.ts` files contain no user-facing progress copy and need no changes beyond verification.

## Files To Inspect

- `components/ProgressTimeline.tsx:48` — `<span className="eyebrow">Analyzing</span>` — the visible "Analyzing" header. **Primary target.**
- `src/util/progress.ts` — CLI/TTY progress reporter; English labels: `batches`, `Elapsed`, `ETA`, `Average`, `sec/batch`, and the piped fallback `batch … elapsed … eta … avg`.
- `src/workflows/customerTopNewsWorkflow.ts:384` — `step: \`LLM batch ${completedBatches}/${totalBatches}\`` — surfaced live in `currentStep`/timeline; other steps in this file are already Russian.
- `lib/jobStore.ts:239,287,290` & `components/ProgressView.tsx` — already Russian; confirm consistency only.
- `app/api/analyze/route.ts`, `app/api/jobs/[jobId]/route.ts`, and the other listed routes — verified to contain no user-facing strings; no change expected.

## Implementation Steps

1. **`components/ProgressTimeline.tsx`** — change the `Analyzing` eyebrow text to Russian, e.g. `Анализ` (or `Идёт анализ`). This is the headline item for the task.
2. **`src/workflows/customerTopNewsWorkflow.ts:384`** — translate `LLM batch ${x}/${y}` to e.g. `LLM-батч ${x}/${y}` (consistent with `LLM-анализ` label in the timeline) so the live step text is Russian.
3. **`src/util/progress.ts`** — translate the CLI reporter strings:
   - `batches` → `батчей`
   - `Elapsed:` → `Прошло:`
   - `ETA:` → `ETA:` (keep, already used in UI)
   - `Average: … sec/batch` → `Среднее: … сек/батч`
   - Piped line: `batch … elapsed … eta … avg` → Russian equivalents.
4. Leave all string interpolation/format logic, ANSI escapes, and numeric formatting untouched — text only.
5. Do not modify the API route files unless a user-facing string is found during inspection (none expected).

## Validation Steps

- `grep -rn "Analyzing"` returns no matches in `components/` / `app/`.
- `grep -n "batch\|Elapsed\|Average\|ETA"` in `src/util/progress.ts` shows no English label words remain (aside from intentional `ETA`/`LLM`).
- `npx tsc --noEmit` (or project typecheck) passes — changes are string-only, so no type impact.
- Run the analyze flow (or inspect `ProgressTimeline`) to confirm the header and live step text render in Russian; run the CLI path to confirm reporter output is Russian.

## Risks

- **Scope mismatch:** the literal "Analyzing" header lives in `components/ProgressTimeline.tsx`, which is *not* in the provided affected-files list, while the listed API routes have no copy. Editing the component is necessary to satisfy the task title; the route files will likely be no-ops.
- **Encoding:** ensure files stay UTF-8 so Cyrillic renders correctly.
- **Consistency:** keep terminology aligned with existing Russian labels (`LLM-анализ`, `Префильтр`, `Тренды`, `Прошло`) to avoid mixed vocabulary.
- **Low risk overall:** all changes are display-string replacements with no logic or API-contract impact.
