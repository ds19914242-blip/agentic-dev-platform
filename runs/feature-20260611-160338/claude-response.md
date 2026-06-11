# Claude Response

I now have a complete picture. Let me present the plan.

---

## Implementation Plan — Task 015: Finish home page (`app/page.tsx`) remaining English

### ⚠️ Discrepancy to flag first

The task title targets **`app/page.tsx`** (home page UI text), and this is consistent with the project's recent commit history (a series of "translate page X to Russian" changes). However, the **"Affected Files" list contains only API routes** (`app/api/**/route.ts`) — none of which is `page.tsx`.

These are contradictory. Based on the task title, the prior-commit pattern, and the rule "prefer the smallest safe implementation," I'm treating the **title as authoritative**: the work is translating the remaining English UI strings in `app/page.tsx` to Russian. The API-route list appears to be an auto-generated artifact and is **out of scope** (translating server error strings there would be a larger, separate change and risks touching logic). If the intent was actually to translate API-route response strings, stop me and I'll re-plan.

### Scope

Single file: **`app/page.tsx`**. No other files (the `Hero` component still has English copy on lines 4–13, but it lives in `components/Hero.tsx`, not `page.tsx` — out of scope per the narrow title, matching how previous tasks were scoped).

### Remaining English strings to translate

The file already has many Russian strings (e.g. lines 75, 116, 147, 274, 279, 299, 309). The leftover English, with proposed translations (matching existing terminology — e.g. `app/reports/page.tsx:95` uses **"Запустить анализ"**):

| Line | Current English | Proposed Russian |
|------|-----------------|------------------|
| 162 | `"Job not found. Please start analysis again."` | `"Задача не найдена. Запустите анализ заново."` |
| 170 | `"Job not found. Please start analysis again."` | `"Задача не найдена. Запустите анализ заново."` |
| 212 | `RSS collection` (label) | `RSS-коллекция` |
| 214–219 | `No collections yet — ` / `create one` / ` and add sources first.` | `Пока нет коллекций — ` / `создайте коллекцию` / ` и сначала добавьте источники.` |
| 228 | `Choose a collection…` | `Выберите коллекцию…` |
| 232 | `({c.sourceIds.length} sources)` | `({c.sourceIds.length} источн.)` (or `источников`) |
| 240 | `Collecting articles…` / `Collect Articles →` | `Сбор статей…` / `Собрать статьи →` |
| 286 | `Run Analysis →` | `Запустить анализ →` |

### Steps

1. Edit each of the strings above in `app/page.tsx` with exact, unique-match replacements. Both line 162 and line 170 are identical strings inside different code branches — they'll need targeted edits using surrounding context to disambiguate (or a `replace_all` since both should get the same translation).
2. Preserve all JSX structure, the `{" "}` whitespace tokens around the inline `<a>` link (lines 216/219), arrows (`→`), ellipses (`…`), and the `{c.sourceIds.length}` expression exactly — only the human-readable text changes.
3. Leave all code, identifiers, API paths, `className` values, and type literals untouched.

### Verification

- `npx tsc --noEmit` (or the project's typecheck) to confirm no JSX/syntax breakage.
- Visual scan / grep of `app/page.tsx` to confirm no remaining `[A-Za-z]`-only user-facing strings remain (excluding code, classNames, and brand terms like "RSS").

### Risk / reversibility

Very low risk — purely string-literal text changes in one client component, no logic touched, trivially reversible. The only judgment calls are translation wording (e.g. `источн.` vs `источников`) and confirming the affected-files discrepancy above.

This is plan-only mode — I've made no changes. Let me know if you'd like me to proceed with the edits, adjust any wording, or if the API-route list was actually the intended scope.

