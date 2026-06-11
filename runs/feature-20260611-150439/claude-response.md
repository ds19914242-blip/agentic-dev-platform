# Claude Response

## Implementation Plan — Task 009: Translate SummaryCards component

### Findings from inspection

The actual translation target is a single file: **`components/SummaryCards.tsx`**. It renders four `KpiCard`s with English display labels. `KpiCard` (`components/KpiCard.tsx`) renders its `label`/`sub` props verbatim as text, and `value` is always a numeric string (`String(...)`) — so only the `label` and `sub` literals are user-facing English needing translation.

The other 11 files in the "Affected Files" list (`src/agents/*`, `src/analysis/*`, `src/llm/client.ts`, `lib/analysisCache.ts`, `components/SourcePicker.tsx`, `components/ExecutiveSummary.tsx`) are part of the type/data dependency chain feeding `ReportData` into this component, but **none contain user-facing strings belonging to SummaryCards**. They require no changes for this task. (`ExecutiveSummary.tsx` has its own "Executive Summary" string, but that belongs to a different component/task, not SummaryCards.)

I confirmed translation terms against already-translated siblings for consistency:
- `Тренды` — already used in `ProgressTimeline.tsx:35`, `app/reports/page.tsx:125`
- `отклонено` — already used in `src/reporting/renderCustomerReport.ts:136`
- `Релевант…` — already used in `app/settings/page.tsx`

### Proposed change (single file: `components/SummaryCards.tsx`)

Translate the four label strings and one sub-label, leaving all logic, props, classes, and numeric values untouched:

| Line | English | Russian |
|------|---------|---------|
| 14 | `label="Collected"` | `label="Собрано"` |
| 16 | `label="Selected"` | `label="Отобрано"` |
| 18 | `sub={`${discarded} discarded`}` | `sub={`${discarded} отклонено`}` |
| 22 | `label="Potentially Relevant"` | `label="Потенциально релевантно"` |
| 26 | `label="Trends"` | `label="Тренды"` |

No other lines change. The `discarded` template interpolation keeps the number first (`5 отклонено`), matching the existing English word-order and the `renderCustomerReport.ts` phrasing.

### Why this is the smallest safe change
- One file, five string literals; fully reversible.
- No type, prop, or control-flow changes — `KpiCard` signature and all CSS accents stay identical.
- No touch to auth, billing, secrets, schema, deployment, or the unrelated backend files in the affected list.

### Verification
- `npx tsc --noEmit` (or the project's build) to confirm no type regressions.
- Visual check of the dashboard summary row to confirm the four cards render the Russian labels.

### Note on scope
The "Affected Files" list is broader than the work this task requires. I recommend confining changes to `components/SummaryCards.tsx`. If you intended the sibling English strings in `components/Dashboard.tsx:60-61,136` and `components/BenchmarkTable.tsx:45-46` (which still read "Collected"/"Selected"/"Potentially Relevant") to be translated as part of this task, let me know — those belong to other components and I've left them out to keep this change minimal and aligned with the per-component epic structure.

This is plan-only — no files were modified.

