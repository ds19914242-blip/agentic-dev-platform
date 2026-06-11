# Approved Plan

The question was dismissed, so I'll proceed with the **smallest safe scope** (recommended defaults) and clearly flag the optional extensions. Here is the plan.

---

# Implementation Plan — Task 017: Finish Profiles page remaining English labels

## Goal
Translate the remaining visible English UI text on the Profiles page (`/profiles`) to Russian, matching conventions already established elsewhere in the app (e.g. `app/reports/page.tsx`).

## Scope decision (defaults applied, since scope question was dismissed)
- **In scope:** visible English labels in `app/profiles/page.tsx`, and the built-in profile **descriptions** in `src/analysis/profiles.ts`.
- **Out of scope (recommended):** the unrelated API route error strings (`analyze`, `benchmark`, `favorites`, `feedback`, `health/db`) and **auth routes** — these are JSON error responses not rendered on the Profiles page, and the rules forbid touching auth unless explicitly required. They are listed in "affected files" at the epic level but are not Profiles-page labels.
- **Must NOT change:** `selectedTopics`, `includeKeywords`, `excludeKeywords` values, and `<option value="...">` values — these are functional keys (matched against `ALL_TOPICS` / the analysis engine / `PerformanceMode`). Only the human-readable display text changes.

## Changes

### File 1 — `app/profiles/page.tsx` (primary)
All edits are display-text only; no logic or state changes.

1. **Line 121** — "built-in" badge: `built-in` → `встроенный`
2. **Line 136** — mode display `{p.defaultMode}` renders raw English (`balanced`). Add a small label map near the top of the file and use it here:
   ```
   const MODE_LABELS: Record<PerformanceMode, string> = {
     fast: "Быстрый", balanced: "Сбалансированный", deep: "Глубокий",
   };
   ```
   Then `· {p.defaultMode}` → `· {MODE_LABELS[p.defaultMode]}`. (`TOP-{p.defaultTopN}` stays — acronym used app-wide.)
3. **Line 192** — `label="Include keywords"` → `label="Ключевые слова: включить"`
4. **Line 206** — `label="Exclude keywords"` → `label="Ключевые слова: исключить"`
5. **Lines 234–236** — option display text only (keep `value=` unchanged), matching `app/reports/page.tsx`:
   - `Fast` → `Быстрый`
   - `Balanced` → `Сбалансированный`
   - `Deep` → `Глубокий`

Note: line 221 `TOP-N` label and line 95–102 ("Профили тем", "+ Новый") are already Russian — no change.

### File 2 — `src/analysis/profiles.ts` (built-in profile descriptions)
Translate the `description` field of all 6 profiles to Russian (these render at `app/profiles/page.tsx:124`). **Keep `name`, `selectedTopics`, `includeKeywords`, `excludeKeywords`, `id` unchanged** — names are recognizable English labels and the keyword/topic arrays are functional. Suggested translations:
- `builtin-ai-security`: "Безопасность ИИ/ML, агентные системы, риски LLM и GenAI."
- `builtin-iam-market`: "Управление идентификацией и доступом, рынок цифровой идентичности."
- `builtin-secops-platforms`: "Операции безопасности, SOC и консолидация платформ."
- `builtin-agentic-ai`: "Автономные агенты, агентные фреймворки и рабочие процессы."
- `builtin-vendor-radar`: "Запуски продуктов, партнёрства, финансирование и M&A среди вендоров."
- `builtin-governance-compliance`: "Регулирование, управление, GRC, приватность и комплаенс."

## Known limitations (call out, do not "fix")
- **Topic chips** (`p.selectedTopics` and `ALL_TOPICS` in the editor) stay English — they are taxonomy keys shared with the analysis engine; translating them would break matching. Out of scope.
- **Built-in profile names** stay English by default (recommended). If full localization of names is desired, that's a one-line-per-profile follow-up.
- **API error strings** (incl. `app/api/profiles/route.ts` "Untitled"/"Invalid JSON." etc.) are not surfaced on the page (the page shows generic toasts like "Не удалось удалить"), so they're excluded.

## Verification
1. `npm run build` (or `tsc`/lint) — pure string edits, should pass with no type changes.
2. Manual: open `/profiles` — confirm badge reads "встроенный", mode reads Russian, keyword section labels and the mode dropdown are Russian, and built-in descriptions are Russian. Confirm topic chips and save/edit/delete still work (functional keys unchanged).

## Risk
Very low — all changes are display strings; no values, props, state, or API contracts change. Fully reversible.

---

If you'd rather **also** translate the built-in profile *names* or the **non-auth API error strings**, tell me and I'll fold them in — otherwise this plan applies the smallest safe scope. This is plan-only; no files were modified.

