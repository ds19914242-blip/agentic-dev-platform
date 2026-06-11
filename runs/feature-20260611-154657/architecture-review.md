# Architecture Review

## Feature Request

Epic task: Task 009 — Translate SummaryCards component

## Planner Input

# Implementation Plan

## Summary

Task 009 translates the user-visible text in the `SummaryCards` component (`components/SummaryCards.tsx`) to Russian, matching the pattern of prior epic tasks (translate only visible UI strings; touch no logic, data, or non-UI files). The component renders four `KpiCard`s with English labels and one sub-label. Only those literal strings need translation.

## Files To Inspect

- `components/SummaryCards.tsx` — the only file to change; contains all the visible English strings.
- `components/KpiCard.tsx` — read-only confirmation that `label` and `sub` props render verbatim (no hardcoded text of its own). Confirmed: it renders props as-is.
- The other "Affected Files" (agents, analysis, llm, cache, SourcePicker, ExecutiveSummary) carry no SummaryCards UI text and are **not** part of this task — leave untouched.

## Implementation Steps

1. In `components/SummaryCards.tsx`, translate the four `KpiCard` `label` values:
   - `"Collected"` → `"Собрано"`
   - `"Selected"` → `"Отобрано"`
   - `"Potentially Relevant"` → `"Потенциально релевантные"`
   - `"Trends"` → `"Тренды"`
2. Translate the `sub` template literal `${discarded} discarded` → `${discarded} отклонено` (keep the interpolated `discarded` variable; only translate the word).
3. Leave all logic, prop names, accent classes, imports, and JSX structure unchanged.

## Validation Steps

- Visually re-read the diff to confirm only string literals changed and JSX/TS structure is intact.
- `npx tsc --noEmit` (or the project's typecheck) — should pass since only string contents changed.
- Run the dev server and view a report/dashboard page that renders `SummaryCards` to confirm the four cards show Russian labels and the "N отклонено" sub-label renders correctly.

## Risks

- **Scope creep**: the broad "Affected Files" list could invite editing unrelated agent/analysis files. Keep the change strictly to `SummaryCards.tsx`.
- **Wording consistency**: ensure terms align with translations already used elsewhere (e.g. "Тренды", "отклонено") so the UI stays coherent across components.
- Very low technical risk — string-only edit with no behavioral change.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Agent/LLM layer: src/agents/summaryBatchAgent.ts
- Agent/LLM layer: src/agents/trendAnalysisAgent.ts
- UI component: components/SummaryCards.tsx
- UI component: components/ExecutiveSummary.tsx
- Agent/LLM layer: src/agents/criteriaBatchAgent.ts
- Other: src/analysis/criteria.ts
- Other: src/analysis/feedbackRanking.ts
- Other: src/analysis/performance.ts
- Other: src/analysis/profiles.ts
- LLM client layer: src/llm/client.ts
- Library/module: lib/analysisCache.ts
- UI component: components/SourcePicker.tsx

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
