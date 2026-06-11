# Approved Plan

## Investigation Summary

The "Translate Feedback page" task follows the same established pattern as the prior epic tasks (NavBar, Hero, Dashboard, Settings/Reading List): **translate user-facing English UI strings into Russian**, leaving logic, identifiers, and non-displayed strings untouched. Each prior task touched only the page component, not the related API routes.

Key findings:
- **`app/feedback/page.tsx`** is the only file with user-facing UI strings. It's currently a mix of English UI text and one stray Russian helper line.
- The NavBar already links to this page with the label **"Обратная связь"** (`components/NavBar.tsx:13`), so the page title should be consistent with that.
- The Settings page (Task 006) already established the canonical Russian vote terminology: `relevant → Релевантно`, `not_relevant → Не релевантно`, `missed_but_relevant → Пропущено, но релевантно`.
- The other 11 affected files (API routes, `feedbackRanking.ts`) contain **only** JSON error strings and code comments — none are rendered in the Feedback UI (the page reads `b.feedback` and swallows errors). They are out of scope, matching how prior tasks left API routes unchanged.
- Date formatting already uses `"ru-RU"` locale — no change needed.

---

## Implementation Plan

**Scope: one file — `app/feedback/page.tsx`. No logic changes, only string literals.**

### 1. `VOTE_LABEL` map (lines 7–11)
| English | Russian |
|---|---|
| `Relevant` | `Релевантно` |
| `Not Relevant` | `Не релевантно` |
| `Missed But Relevant` | `Пропущено, но релевантно` |

This map drives both the filter chips and the per-item badges, so translating it here covers both usages.

### 2. Header block (lines 40–47)
- `h1` "Feedback Center" → **"Центр обратной связи"** (consistent with NavBar's "Обратная связь").
- Subtitle "Your relevance votes shape future rankings (see Settings → Feedback Influence)." → **"Ваши оценки релевантности влияют на будущее ранжирование (см. Настройки → Влияние отзывов)."** (matches Settings page terminology "Влияние отзывов").
- The existing Russian line at 44–46 ("Здесь собраны ваши оценки релевантности статей.") is already Russian. **Recommendation:** remove it, since after translating the subtitle it becomes redundant. (Smallest-safe alternative: leave it as-is — no functional impact. I lean toward removing for polish, but will keep it if minimal-change is preferred.)

### 3. KpiCard labels (lines 50–56)
- `label="Relevant"` → `label="Релевантно"`
- `label="Not Relevant"` → `label="Не релевантно"`
- `label="Missed But Relevant"` → `label="Пропущено, но релевантно"`

(These are passed as literals separately from `VOTE_LABEL`, so each must be updated individually.)

### 4. Filter chips (line 66)
- `f === "all" ? "All" : VOTE_LABEL[f]` → `f === "all" ? "Все" : VOTE_LABEL[f]`

### 5. Empty states (line 75)
- "No feedback yet — vote on articles in a report." → **"Пока нет отзывов — оценивайте статьи в отчёте."**
- "Nothing for this filter." → **"Ничего по этому фильтру."**

### Out of scope (intentionally unchanged)
- API routes (`app/api/feedback/route.ts` and the other 10 routes) — their `"Invalid JSON."` / `"Invalid vote."` strings are not surfaced in the Feedback UI; consistent with prior tasks leaving API routes untranslated.
- `src/analysis/feedbackRanking.ts` — comments/logic only, no UI strings.
- The `"ru-RU"` date locale, `FeedbackVote` keys, CSS classes, and all logic.

### Verification
- `npm run build` / `tsc` to confirm no type or syntax breakage (string-only edits, so risk is minimal).
- Visually confirm the Feedback page renders entirely in Russian and the filter chips/badges still map correctly.

### Reversibility
Single-file, literal-only change — trivially revertible via `git checkout app/feedback/page.tsx`.

---

**One open decision** worth your call before I implement: whether to **remove** the now-redundant Russian helper line (44–46) or **keep** it. My recommendation is to remove it. Let me know, and note this is plan-only — I have not modified any files.

