# Claude Response

I attempted to confirm scope but didn't get a response, so I'll present the plan using the **recommended defaults** and document those decisions explicitly. Since this is plan-only mode, I'm not modifying any files.

---

# Implementation Plan — Task 017: Finish Profiles page remaining English labels

## Goal
Translate the remaining English **visible UI text** on the Profiles page to Russian, consistent with the rest of the app (which is being progressively localized). Keep all functional identifiers (mode values, topic strings, keywords, IDs) unchanged.

## Scope decisions (recommended defaults applied)
- **Built-in profile names + descriptions** (`src/analysis/profiles.ts`): translate both. They render directly on the page. IDs, `selectedTopics`, `includeKeywords`, `excludeKeywords` stay **unchanged** — they're functional matching identifiers validated against `ALL_TOPICS`/used by the analysis pipeline; translating them would break filtering.
- **API route error strings** (profiles/analyze/benchmark/favorites/feedback/health/auth routes): **out of scope.** They return JSON not surfaced on the Profiles page (the page uses its own Russian toasts), the repo convention is "visible UI text only," and auth routes are protected by the task rules. No changes to any `app/api/**` file.

> If you'd prefer a different scope (e.g. include non-auth API strings, or leave profile names English), say so and I'll revise.

## Existing convention to follow
- No i18n library — Russian strings are hardcoded inline (as in `app/profiles/page.tsx` already: "Профили тем", "Новый профиль", etc.).
- Mode labels are already translated on the reports page (`app/reports/page.tsx:77-79`): **fast→Быстрый, balanced→Сбалансированный, deep→Глубокий**. Reuse these exact strings.

---

## Changes

### File 1 — `app/profiles/page.tsx`

1. **"built-in" badge** (line 120): `built-in` → `встроенный`

2. **Mode display in list** (line 136): `TOP-{p.defaultTopN} · {p.defaultMode}` renders raw English mode. Add a small label map near the top of the file:
   ```ts
   const MODE_LABELS: Record<PerformanceMode, string> = {
     fast: "Быстрый",
     balanced: "Сбалансированный",
     deep: "Глубокий",
   };
   ```
   Then render `TOP-{p.defaultTopN} · {MODE_LABELS[p.defaultMode]}`. (`PerformanceMode` is already imported.)

3. **Keyword section labels** (the two `<KwRow label=...>` props):
   - Line 192: `"Include keywords"` → `"Ключевые слова (включить)"`
   - Line 206: `"Exclude keywords"` → `"Ключевые слова (исключить)"`

4. **Mode `<select>` options** (lines 234-236): translate the **visible label text only**, keep `value` attributes unchanged so the API contract (`isPerformanceMode`) still holds:
   - `<option value="fast">Быстрый</option>`
   - `<option value="balanced">Сбалансированный</option>`
   - `<option value="deep">Глубокий</option>`

5. **"TOP-N" label** (line 221): **leave as-is.** "TOP-N" is a technical term used consistently across the app (benchmark/reports/configure) and the subtitle already references it in Russian context. Translating it would be inconsistent. (Flagging as a deliberate no-change.)

*Already Russian (no change needed):* page title, subtitle, "+ Новый", "Изм.", "Удал.", "Темы", placeholders "Название"/"Описание"/"добавить…", "Сохранить"/"Создать"/"Отмена", toasts, and the ConfirmModal strings.

### File 2 — `src/analysis/profiles.ts`

Translate `name` and `description` for all 6 built-in profiles. Keep every other field byte-for-byte. Proposed strings:

| id | name → | description → |
|---|---|---|
| builtin-ai-security | Безопасность ИИ | Безопасность ИИ/ML, агентные системы, риски LLM и генеративного ИИ. |
| builtin-iam-market | Рынок IAM | Управление идентификацией и доступом, движения рынка цифровой идентичности. |
| builtin-secops-platforms | Платформы SecOps | Операции безопасности, SOC и консолидация платформ. |
| builtin-agentic-ai | Агентный ИИ | Автономные агенты, агентные фреймворки и агентные рабочие процессы. |
| builtin-vendor-radar | Радар вендоров | Запуски продуктов, партнёрства, финансирование и сделки M&A среди вендоров. |
| builtin-governance-compliance | Управление и комплаенс | Регулирование, управление, GRC, приватность и комплаенс. |

> Note: a profile's `name` is also passed as a run label into the analysis/reports flow (`startAnalysis` → reports). Translating names means new runs from these built-ins show Russian labels in reports — this is the intended, consistent behavior, but it's the one cross-page effect worth being aware of.

---

## Out of scope / explicitly untouched
- All `app/api/**` routes (incl. both auth routes) — no changes.
- `src/analysis/criteria.ts` `ALL_TOPICS` and the topic chips that render them — functional values, not listed as affected, stay English.
- `includeKeywords` / `excludeKeywords` — functional matching terms (also never displayed for built-ins, which can't be edited).
- DB seed data in `lib/storage/postgres.ts` / `scripts/dbInit.ts` — not in affected files; built-in profiles fall back to the code definitions, and seeding is idempotent/keyed by `id`, so the name/description changes surface in the UI without a schema or seed change.

## Verification
- `npm run build` / typecheck (the `MODE_LABELS` map must cover all `PerformanceMode` values — TypeScript will enforce this).
- Manually load `/profiles`: confirm badge reads "встроенный", built-in cards show Russian names/descriptions + Russian mode label, editor shows Russian keyword labels and mode options, and saving/selecting a mode still works (values unchanged).
- Confirm no remaining English in the rendered page except the intentional "TOP-N" term and topic chips.

## Risk & reversibility
Low. All changes are display-string edits plus one small label map; no logic, API contracts, IDs, or stored values change. Fully reversible per-line. Two files touched (`app/profiles/page.tsx`, `src/analysis/profiles.ts`).

---

**Stopping here per plan-only mode — no files modified.** Let me know if you want the scope adjusted (e.g. include non-auth API error strings, or keep profile names in English) before implementation.

