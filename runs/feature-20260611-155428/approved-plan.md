# Approved Plan

I have everything I need. The task is narrow and well-scoped. Here's my plan.

## Implementation Plan — Task 010: Translate StrategicSignals component

### Findings

- **`components/StrategicSignals.tsx`** is the only file that needs changes. The section heading (`Стратегические сигналы`, line 15) is **already** translated. The remaining English user-visible strings are the 5 group `name` labels (lines 5–9), which render as the `<h3>` card titles (line 24).
- The `icon` glyphs and the data values (from `trends.strategicSignals.*`) are not UI labels — leave them untouched.
- The group `name` doubles as the React `key` (line 19) and the display label. Translating it is safe: the names stay unique, and the key is internal-only (not persisted, not referenced elsewhere).
- **No type changes:** the `TrendAnalysis` field names (`productLaunches`, etc. in `src/types/report.ts`) are data properties, not display text — untouched.
- **Out of scope (intentionally not modified):**
  - `src/reporting/renderCustomerReport.ts` — server-side markdown report (`## Strategic Signals`), not the UI component; not in this task's intent and changing it would broaden scope.
  - `components/SourcePicker.tsx` and the 9 `app/api/**` routes listed as "affected files" — these are the broader epic's file list. SourcePicker has English labels but belongs to a different component task; the API routes contain no StrategicSignals UI text. Per the "smallest safe implementation" rule, I will not touch them.

### Change (single file: `components/StrategicSignals.tsx`)

Translate the 5 `name` strings in the `groups` array (lines 5–9):

| Line | Current | Proposed Russian |
|------|---------|------------------|
| 5 | `Product Launches` | `Запуски продуктов` |
| 6 | `Partnerships` | `Партнёрства` |
| 7 | `AI Initiatives` | `ИИ-инициативы` |
| 8 | `IAM / Governance` | `IAM / Управление` |
| 9 | `SecOps / Platform` | `SecOps / Платформа` |

(Technical acronyms `IAM` and `SecOps` are kept as-is, matching common Russian industry usage.)

### Verification

- Visual: render the dashboard and confirm the 5 card titles display the Russian labels with counts/glyphs intact.
- `npm run build` / typecheck to confirm no TS breakage (no type or key contract changed).

### Risk

Very low — 5 string literals in one presentational component; no logic, data, or type changes; fully reversible.

**This is plan-only — no files modified.** One open question worth confirming before implementation: the exact wording of the translations above (e.g., should "Partnerships" become "Партнёрства и интеграции" to mirror the report's "Partnerships / Integrations", or stay literal as "Партнёрства"?). I've matched the current UI's literal text. Let me know if you'd prefer different phrasing.

