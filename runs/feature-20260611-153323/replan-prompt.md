# Replan Failed Implementation

The implementation failed validation.

Your job:
1. Analyze the validation failure.
2. Identify the most likely root cause.
3. Produce a minimal fix plan.
4. Apply the fix directly.
5. Do not redesign the feature.
6. Do not touch auth, billing, secrets, database schema, or deployment config.

# Feature Request

Epic task: Task 017 — Finish Profiles page remaining English labels

# Approved Plan

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



# Implementation Response

# Claude Implementation Response

Dependencies aren't installed in this worktree (no `node_modules`), so `npx tsc --noEmit` can't run. The changes are pure display-string edits plus one type-annotated constant (`MODE_LABELS: Record<PerformanceMode, string>`, using the already-imported `PerformanceMode`), so no type-shape changes were introduced.

## Changed files

**`app/profiles/page.tsx`**
- Added `MODE_LABELS` map (`fast`→Быстрый, `balanced`→Сбалансированный, `deep`→Глубокий).
- Badge `built-in` → `встроенный`.
- Mode display `{p.defaultMode}` → `{MODE_LABELS[p.defaultMode]}` (TOP-N unchanged).
- `KwRow` labels: `Include keywords` → `Ключевые слова: включить`; `Exclude keywords` → `Ключевые слова: исключить`.
- Mode `<option>` display text → Быстрый / Сбалансированный / Глубокий (`value=` attributes unchanged).

**`src/analysis/profiles.ts`**
- Translated the `description` field of all 6 built-in profiles to Russian. `id`, `name`, `selectedTopics`, `includeKeywords`, `excludeKeywords`, `defaultMode`, `defaultTopN` all left unchanged.

## Out of scope (per plan)
- Topic chips / `ALL_TOPICS` (taxonomy keys), built-in profile names, and non-auth API error strings — left as-is.

## Risks
- **Very low.** All edits are human-readable display strings; no functional keys, `value=` attributes, props, state, or API contracts changed. Fully reversible.
- **Verification gap:** I could not run `npm run typecheck` because `node_modules` is absent in this worktree. The only non-string addition is the `MODE_LABELS` constant, which is type-checked against the imported `PerformanceMode` union and covers all three members exhaustively, so it should compile cleanly. If you want, I can `npm install` and run the typecheck to confirm.


# Validation Report

# Validation Result

## Overall Result

failed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: failed

Timed Out: False

Exit Code: 1

### STDOUT

```text

[41m                                                                               [0m
[41m[37m                This is not the tsc command you are looking for                [0m
[41m                                                                               [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: failed

Timed Out: False

Exit Code: 127

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build


```

### STDERR

```text
sh: next: command not found

```

