# Approved Plan

I now have what I need. The task is scoped to translating the **SummaryCards** component's visible UI text to Russian, following the convention already established in this repo (commit `f12d042` translated visible strings only, leaving logic/class names untouched).

## Findings

The only file with user-visible text belonging to the SummaryCards component is **`components/SummaryCards.tsx`**. The other files in the "Affected Files" list (`src/agents/*`, `src/analysis/*`, `src/llm/client.ts`, `lib/analysisCache.ts`, `components/ExecutiveSummary.tsx`, `components/SourcePicker.tsx`) are backend logic or *other* components — none of their strings are rendered by SummaryCards, so translating them would exceed the task scope ("Translate SummaryCards component") and the "smallest safe change" rule.

SummaryCards renders four `KpiCard`s. The visible strings are the `label` and `sub` props (the `value` props are numbers, and `accent`/className strings are not user-facing).

## Implementation Plan

**File: `components/SummaryCards.tsx` — translate 5 visible strings only**

| Line | Current (English) | Proposed (Russian) |
|------|-------------------|--------------------|
| 14 | `label="Collected"` | `label="Собрано"` |
| 16 | `label="Selected"` | `label="Выбрано"` *(matches reports page)* |
| 18 | `sub={`${discarded} discarded`}` | `sub={`${discarded} отклонено`}` |
| 22 | `label="Potentially Relevant"` | `label="Потенциально релевантные"` |
| 26 | `label="Trends"` | `label="Тренды"` *(matches reports page)* |

**What stays untouched:** all logic, prop names, variable names, `accent` color classes, `className` strings, imports, and the `KpiCard` component itself (it's a generic presentational component — translating it would affect other usages).

**Consistency notes:** "Selected"→"Выбрано" and "Trends"→"Тренды" reuse the exact translations already committed in `app/reports/page.tsx`, keeping terminology uniform across the dashboard.

## Verification (after applying)
- `npx tsc --noEmit` (or the project's typecheck) — string-only edits should not affect types.
- Visually confirm the four KPI cards render the Russian labels.

## Scope / uncertainty
- **Reversibility:** trivial — 5 string literals, fully revertible.
- **Out of scope by design:** `ExecutiveSummary.tsx` ("Executive Summary") and `SourcePicker.tsx` ("Upload TXT file", "RSS Collection") contain English UI text but are separate components with their own epic tasks; I've left them out to honor the SummaryCards-only scope. If you'd actually like those two components folded into this change, let me know and I'll extend the plan.

No files were modified (plan-only mode). Ready to implement on your go-ahead.

