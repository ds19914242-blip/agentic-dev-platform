# Approved Plan

I have everything I need. Here's my analysis and plan.

## Findings

**Target language:** Russian (established by prior tasks 001/003/004/006, e.g. Hero "Intelligence Platform" → "Платформа аналитики").

Of the 12 affected files, only **two contain untranslated user-facing strings** that fit this task ("ExecutiveSummary and report section headers"). The rest are either already in Russian, or pure logic/keywords that **must not** be translated.

---

## Implementation Plan — Task 011

### Changes (2 files)

**1. `components/ExecutiveSummary.tsx` (line 8)**

The section header eyebrow is the only English string:
```
- <span className="eyebrow">Executive Summary</span>
+ <span className="eyebrow">Краткое резюме</span>
```
(The `—` empty-state placeholder on line 11 stays as-is.)

**2. `components/SummaryCards.tsx` (lines 14–26)** — the report's KPI summary section labels:

| English | Proposed Russian |
|---|---|
| `Collected` (l.14) | `Собрано` |
| `Selected` (l.16) | `Отобрано` |
| `` `${discarded} discarded` `` (l.18) | `` `${discarded} отброшено` `` |
| `Potentially Relevant` (l.23) | `Потенциально релевантные` |
| `Trends` (l.26) | `Тренды` |

These are pure string swaps inside JSX props passed to `KpiCard`; no logic, types, or layout change. `KpiCard.tsx` needs no edit (it just renders the props).

---

### Files requiring NO change (with justification)

- **`src/agents/summaryBatchAgent.ts`, `trendAnalysisAgent.ts`, `criteriaBatchAgent.ts`** — system prompts are **already in Russian**; the LLM already emits `executiveSummary`/trend text in Russian at runtime. No user-facing English.
- **`src/analysis/criteria.ts`** — the include/exclude keyword lists and `TOPIC_KEYWORDS` are **English matching tokens** compared against English article text in the prefilter/LLM rubric. Translating them would **break relevance filtering**. Leave untouched.
- **`src/analysis/profiles.ts`** — profile `name`/`description` are English, but they are configure-screen content, **not report section headers**, and not the focus of this task. Translating risks scope creep and depends on stored profile IDs. Out of scope.
- **`src/analysis/feedbackRanking.ts`, `performance.ts`, `src/llm/client.ts`, `lib/analysisCache.ts`** — internal logic, comments, and `console.warn` diagnostics only. No user-facing UI strings.
- **`app/api/report/[id]/docx/route.ts`** — only string is the API error `"Report not found."` (a JSON error, not a section header). The actual DOCX section headers live in `lib/export/docx.ts`, which is **not** in the affected-files list.

---

### Uncertainties to flag

1. **"Executive Summary" wording** — I propose `Краткое резюме`. Alternatives: `Резюме для руководства` (more literal) or `Главные выводы`. Easy to change; flagging since it's a judgment call.
2. **Other report section headers** (e.g. `Intelligence Report`, `Potentially Relevant`, chart titles) live in **`components/Dashboard.tsx`**, which is **not** in this task's affected files (it's partially translated already — appears handled by a different epic task). I've kept this task scoped to the two listed components rather than expanding into Dashboard.tsx.
3. **DOCX export headers** — if "report section headers" was meant to include the Word export, the real target is `lib/export/docx.ts` (unlisted), not the route. I recommend **not** expanding scope unless you confirm.

### Verification after edit
- `npm run build` / `tsc` (string-only changes — should compile cleanly).
- Visually confirm the report dashboard renders the Russian KPI labels and "Краткое резюме" header.

No files have been modified. Awaiting your go-ahead (and any preference on the "Executive Summary" wording / whether to extend to Dashboard.tsx or docx.ts).

