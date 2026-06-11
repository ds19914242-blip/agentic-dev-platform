# Approved Plan

I have enough to write the plan. Let me confirm what's actually user-facing in the broader affected list by checking the docx route's only English string context — already seen (`"Report not found."`, an API error, not a report section header).

## Implementation Plan — Task 011: Translate ExecutiveSummary and report section headers

### Findings from inspecting the affected files

This repo is mid-way through an incremental English→Russian translation of **visible UI text only** (e.g. `StatsPanel.tsx` rows and `Dashboard.tsx` line 180 are already Russian, while sibling headers remain English). Task 011's job is to finish the translation for the two in-scope **report display components**.

I inspected all 12 affected files. Only **two** contain user-facing English strings; the rest fall into three "no-change" buckets:

| File | User-facing English? | Action |
|---|---|---|
| `components/ExecutiveSummary.tsx` | Yes — `"Executive Summary"` eyebrow | **Edit** |
| `components/SummaryCards.tsx` | Yes — 4 KPI labels + sub text | **Edit** |
| `src/agents/summaryBatchAgent.ts` | No — prompts already Russian | none |
| `src/agents/trendAnalysisAgent.ts` | No — prompts already Russian | none |
| `src/agents/criteriaBatchAgent.ts` | No — prompts already Russian | none |
| `src/analysis/criteria.ts` | No — English keywords/topic keys are matching data (changing them would break the prefilter/LLM rubric) | none |
| `src/analysis/feedbackRanking.ts` | No — pure logic + comments | none |
| `src/analysis/performance.ts` | No — enums/presets | none |
| `src/analysis/profiles.ts` | English profile `name`/`description`, but these are **configure-screen** strings, not report section headers — out of scope | none |
| `src/llm/client.ts` | No | none |
| `lib/analysisCache.ts` | No | none |
| `app/api/report/[id]/docx/route.ts` | Only `"Report not found."` (JSON API error, not a rendered report header) — out of scope | none |

The other files in the affected list appear to be included as **subsystem context** (the report-generation pipeline) rather than edit targets. The actual report section headers in the broader app live in `Dashboard.tsx`, `TrendsPanel.tsx`, `StrategicSignals.tsx`, `StatsPanel.tsx` and the export renderers (`lib/export/docx.ts`, `pdf.ts`) — **none of which are in scope for this task**, so I will leave them untouched.

### Planned edits

**1. `components/ExecutiveSummary.tsx` (line 8)**
```
<span className="eyebrow">Executive Summary</span>
→
<span className="eyebrow">Краткое резюме</span>
```
(Alternative wording: `Ключевые выводы`, which matches the list's content — the prompt generates "ключевые выводы". I recommend `Краткое резюме` as the closest business equivalent of "Executive Summary", but this is the one wording choice worth confirming.)

**2. `components/SummaryCards.tsx` (lines 14–26)** — translate the four `KpiCard` labels and the sub text:
- `label="Collected"` → `label="Собрано"`
- `label="Selected"` → `label="Отобрано"`
- `` sub={`${discarded} discarded`} `` → `` sub={`${discarded} отклонено`} ``
- `label="Potentially Relevant"` → `label="Потенциально релевантные"`
- `label="Trends"` → `label="Тренды"`

These terms match the already-translated vocabulary in `StatsPanel.tsx` (e.g. "Отклонено LLM", "Совпало с критериями").

### Safety / blast radius
- Both files are pure presentational components; no logic, props, or types change — only JSX text literals.
- The strings `"Executive Summary"`, `"Potentially Relevant"`, etc. also appear in `lib/export/docx.ts`, `lib/export/pdf.ts`, `src/reporting/renderCustomerReport.ts`, and `Dashboard.tsx`, but each is an **independent local literal**, not a shared constant — editing the two components has no effect on them and no test couples to these strings.
- No auth/billing/secrets/schema/config touched. Fully reversible (revert two small diffs).

### One open question
The single judgment call is the exact Russian rendering of "Executive Summary" (`Краткое резюме` vs `Ключевые выводы`). Everything else has an unambiguous, style-consistent translation. I can proceed with `Краткое резюме` unless you prefer otherwise.

Per the plan-only mode, I've made no file changes and am stopping here.

