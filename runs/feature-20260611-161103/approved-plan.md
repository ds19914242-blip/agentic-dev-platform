# Approved Plan

I've inspected all affected files. Here's my analysis and implementation plan.

## Summary of findings

The task title — **"Translate ExecutiveSummary and report section headers"** — is the precise scope. After inspecting every affected file, only **two** of them contain untranslated, user-visible English strings in the report UI. The rest of the "affected files" list is the report's data-flow dependency closure (agents, analysis logic, LLM client, cache, docx route) and either **already emits Russian** or **contains no UI strings**.

### Per-file disposition of the affected files

| File | Contains report UI text to translate? | Action |
|---|---|---|
| `components/ExecutiveSummary.tsx` | ✅ `"Executive Summary"` eyebrow | **Edit** |
| `components/SummaryCards.tsx` | ✅ KPI labels (`Collected`, `Selected`, `discarded`, `Potentially Relevant`, `Trends`) | **Edit** |
| `src/agents/summaryBatchAgent.ts` | No — prompts already in Russian | None |
| `src/agents/trendAnalysisAgent.ts` | No — prompts already in Russian | None |
| `src/agents/criteriaBatchAgent.ts` | No — prompts already in Russian | None |
| `src/analysis/criteria.ts` | No — English topic keys are matching identifiers / cache-key inputs (changing them breaks keyword matching, profiles, cache) | None |
| `src/analysis/feedbackRanking.ts` | No — pure logic | None |
| `src/analysis/performance.ts` | No — mode identifiers | None |
| `src/analysis/profiles.ts` | No — profile names/descriptions are config UI, not report section headers | None |
| `src/llm/client.ts` | No — client setup | None |
| `lib/analysisCache.ts` | No — caching logic | None |
| `app/api/report/[id]/docx/route.ts` | No — only an API error string + filename; actual docx headers live in `lib/export/docx.ts` (not in scope) | None |

## Planned edits

### 1. `components/ExecutiveSummary.tsx` (line 8)
Translate the section eyebrow:
```diff
- <span className="eyebrow">Executive Summary</span>
+ <span className="eyebrow">Краткая сводка</span>
```
(Recommended: **"Краткая сводка"**. Alternative: "Ключевые выводы" — the underlying field is described as «ключевые выводы о рынке» in the agent prompt.)

### 2. `components/SummaryCards.tsx` (lines 14–26)
Translate the four KPI labels and the `discarded` sub-label, matching terminology already used elsewhere in the report (`StatsPanel`, `Dashboard`):
```diff
- <KpiCard label="Collected" value={String(s.totalFound)} accent="bg-slate-400" />
+ <KpiCard label="Собрано" value={String(s.totalFound)} accent="bg-slate-400" />
  <KpiCard
-   label="Selected"
+   label="Отобрано"
    value={String(selected)}
-   sub={`${discarded} discarded`}
+   sub={`${discarded} отклонено`}
    accent="bg-emerald-500"
  />
  <KpiCard
-   label="Potentially Relevant"
+   label="Потенциально релевантные"
    accent="bg-sky-500"
  />
- <KpiCard label="Trends" value={String(trends)} accent="bg-violet-500" />
+ <KpiCard label="Тренды" value={String(trends)} accent="bg-violet-500" />
```
("Тренды" matches the existing «Топ-5 рыночных трендов» panel; "Отобрано"/"отклонено" match `StatsPanel`.)

These are string-only changes — no logic, types, props, or layout touched. `KpiCard` renders `label`/`sub` as plain text (verified), so translation is sufficient. Fully reversible.

## Verification
- `npm run build` / `tsc` (string-only changes should not affect types).
- Visually confirm the dashboard renders the translated Executive Summary header and KPI cards.

## ⚠️ Scope uncertainty to confirm before implementing

"Report section headers" could be read more broadly than the two affected files. There are **other still-English report headers that live in files NOT on the affected-files list**, so under the "inspect the affected files / smallest safe change" rules I've left them out:

- `components/Dashboard.tsx`: `"Intelligence Report"` eyebrow, the `Collected · Selected · Potentially Relevant · Trends` line, `"Generated:"`, the `"Potentially Relevant"` `<h2>` + its description, and the four `ChartCard` titles (`Category Distribution`, `Matched vs Excluded`, `Exclusion Reasons`, `Source Distribution`).
- `components/StatsPanel.tsx`: `"Processing"` and `"Performance"` headings.
- `lib/export/docx.ts`: all `.docx` export headings (`Executive Summary`, `Top Market Trends`, `Strategic Signals`, etc.) — reached via the affected `docx/route.ts` but defined here.

My plan covers exactly the two affected UI files named by the task. If you intend the broader set of report headers too, those extra files need to be explicitly added to scope — let me know and I'll extend the plan.

I've stopped here per plan-only mode and made no file changes. Want me to (a) proceed with just the two affected files, or (b) extend the plan to the broader report headers above?

