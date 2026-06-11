# QA Plan

## Feature Request

Epic task: Task 009 — Translate SummaryCards component

## Based On Plan

# Implementation Plan

## Summary

Task 009 translates the user-facing English strings in the `SummaryCards` component to Russian, matching the established pattern used in prior epic tasks (NavBar, Hero, Dashboard, Reading List) where English UI literals are replaced inline with Russian text directly in the JSX. The only file containing translatable user-facing strings for this component is `components/SummaryCards.tsx`. The remaining "Affected Files" are dependencies/context (data types and producers) — they require **no changes**, only inspection to confirm none emit additional user-facing literals rendered through `SummaryCards`.

## Files To Inspect

- **`components/SummaryCards.tsx`** — primary target; contains the 5 KPI labels/sub-strings to translate.
- `components/KpiCard.tsx` — confirmed pass-through; renders `label`/`value`/`sub` props verbatim, no hardcoded strings of its own. No change needed.
- `lib/dashboard.ts` (`ReportData` type) — confirm field shapes (`processingStats`, `topNews`, `trendAnalysis`, etc.); no UI strings.
- `src/agents/summaryBatchAgent.ts`, `src/agents/trendAnalysisAgent.ts`, `src/agents/criteriaBatchAgent.ts` — data producers; confirm they don't inject display literals into the values shown by these cards.
- `src/analysis/criteria.ts`, `feedbackRanking.ts`, `performance.ts`, `profiles.ts` — analysis helpers feeding counts; inspect only to confirm no rendered strings.
- `src/llm/client.ts`, `lib/analysisCache.ts`, `components/SourcePicker.tsx`, `components/ExecutiveSummary.tsx` — listed as affected; verify out of scope for *this* component's translation (e.g. `ExecutiveSummary`'s "Executive Summary" eyebrow belongs to a separate task unless explicitly bundled).

## Implementation Steps

1. In `components/SummaryCards.tsx`, translate the four `KpiCard` `label` props and the one `sub` string:
   - `"Collected"` → `"Собрано"`
   - `"Selected"` → `"Отобрано"`
   - `` `${discarded} discarded` `` → `` `${discarded} отклонено` ``
   - `"Potentially Relevant"` → `"Потенциально релевантно"`
   - `"Trends"` → `"Тренды"`
2. Leave all `value`, `accent`, computation logic, imports, and component structure untouched — only string literals change.
3. Confirm Russian terminology is consistent with translations already shipped in Dashboard/Hero (e.g. analytics vocabulary) for a uniform glossary.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) — ensure no type/JSX breakage.
- Run the lint/build step used by prior tasks (`npm run build` or `next build`) to confirm the component compiles.
- Visually verify the Dashboard page (`app/dashboard/page.tsx`, which renders `SummaryCards`) shows the four cards with Russian labels and the "N отклонено" sub-text.
- Confirm no other component or test references the old English literals (quick grep for `"Collected"`, `"Potentially Relevant"`, `"discarded"`).

## Risks

- **Scope creep**: The broad "Affected Files" list could imply translating agents/analysis/`ExecutiveSummary` too. Recommend keeping this task strictly to `SummaryCards.tsx`; `ExecutiveSummary`'s "Executive Summary" eyebrow is a separate component and likely a different epic task.
- **Glossary inconsistency**: "Selected"/"Potentially Relevant" may already be translated differently elsewhere; align wording to avoid divergent terms across pages.
- **Layout overflow**: Russian strings are longer than English (e.g. "Потенциально релевантно"); verify the 2-col/4-col grid cards don't visually clip on smaller breakpoints.
- **No test coverage**: Repository has no detected tests, so validation relies on typecheck/build plus manual visual confirmation.


## Based On Architecture Review

# Architecture Review

## Feature Request

Epic task: Task 009 — Translate SummaryCards component

## Planner Input

# Implementation Plan

## Summary

Task 009 translates the user-facing English strings in the `SummaryCards` component to Russian, matching the established pattern used in prior epic tasks (NavBar, Hero, Dashboard, Reading List) where English UI literals are replaced inline with Russian text directly in the JSX. The only file containing translatable user-facing strings for this component is `components/SummaryCards.tsx`. The remaining "Affected Files" are dependencies/context (data types and producers) — they require **no changes**, only inspection to confirm none emit additional user-facing literals rendered through `SummaryCards`.

## Files To Inspect

- **`components/SummaryCards.tsx`** — primary target; contains the 5 KPI labels/sub-strings to translate.
- `components/KpiCard.tsx` — confirmed pass-through; renders `label`/`value`/`sub` props verbatim, no hardcoded strings of its own. No change needed.
- `lib/dashboard.ts` (`ReportData` type) — confirm field shapes (`processingStats`, `topNews`, `trendAnalysis`, etc.); no UI strings.
- `src/agents/summaryBatchAgent.ts`, `src/agents/trendAnalysisAgent.ts`, `src/agents/criteriaBatchAgent.ts` — data producers; confirm they don't inject display literals into the values shown by these cards.
- `src/analysis/criteria.ts`, `feedbackRanking.ts`, `performance.ts`, `profiles.ts` — analysis helpers feeding counts; inspect only to confirm no rendered strings.
- `src/llm/client.ts`, `lib/analysisCache.ts`, `components/SourcePicker.tsx`, `components/ExecutiveSummary.tsx` — listed as affected; verify out of scope for *this* component's translation (e.g. `ExecutiveSummary`'s "Executive Summary" eyebrow belongs to a separate task unless explicitly bundled).

## Implementation Steps

1. In `components/SummaryCards.tsx`, translate the four `KpiCard` `label` props and the one `sub` string:
   - `"Collected"` → `"Собрано"`
   - `"Selected"` → `"Отобрано"`
   - `` `${discarded} discarded` `` → `` `${discarded} отклонено` ``
   - `"Potentially Relevant"` → `"Потенциально релевантно"`
   - `"Trends"` → `"Тренды"`
2. Leave all `value`, `accent`, computation logic, imports, and component structure untouched — only string literals change.
3. Confirm Russian terminology is consistent with translations already shipped in Dashboard/Hero (e.g. analytics vocabulary) for a uniform glossary.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) — ensure no type/JSX breakage.
- Run the lint/build step used by prior tasks (`npm run build` or `next build`) to confirm the component compiles.
- Visually verify the Dashboard page (`app/dashboard/page.tsx`, which renders `SummaryCards`) shows the four cards with Russian labels and the "N отклонено" sub-text.
- Confirm no other component or test references the old English literals (quick grep for `"Collected"`, `"Potentially Relevant"`, `"discarded"`).

## Risks

- **Scope creep**: The broad "Affected Files" list could imply translating agents/analysis/`ExecutiveSummary` too. Recommend keeping this task strictly to `SummaryCards.tsx`; `ExecutiveSummary`'s "Executive Summary" eyebrow is a separate component and likely a different epic task.
- **Glossary inconsistency**: "Selected"/"Potentially Relevant" may already be translated differently elsewhere; align wording to avoid divergent terms across pages.
- **Layout overflow**: Russian strings are longer than English (e.g. "Потенциально релевантно"); verify the 2-col/4-col grid cards don't visually clip on smaller breakpoints.
- **No test coverage**: Repository has no detected tests, so validation relies on typecheck/build plus manual visual confirmation.


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


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- components/SummaryCards.tsx
- components/ExecutiveSummary.tsx
- src/agents/criteriaBatchAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts
- lib/analysisCache.ts
- components/SourcePicker.tsx

## Required Command

```bash
npx tsc --noEmit
```