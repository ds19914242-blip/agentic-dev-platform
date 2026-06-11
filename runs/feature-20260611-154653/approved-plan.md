# Approved Plan

## Implementation Plan — Task 005: Translate Settings page

### Findings from inspection

- **`app/settings/page.tsx`** is the only file with user-visible UI text for this page. All strings are hardcoded in the component (the `OPTIONS` array, headings, descriptions, list items) plus two toast messages.
- **`app/api/settings/route.ts`** and the other 10 API routes contain only `error` strings like `"Invalid JSON."`. These are **not** surfaced to the user on the Settings page — the page catches failures and shows its own hardcoded toast (`"Failed to save"`). So no UI translation flows through the API layer.
- **Precedent:** the two prior translation commits (reports page `f12d042`, feedback page) each modified **only** the page's `.tsx` component, not any API route. I'll follow that established convention.

### Scope decision

Translate **only** `app/settings/page.tsx`. Leave all API routes untouched. This is the smallest safe change, matches prior tasks, and complies with the rule against modifying more than needed (no auth/billing/secrets/schema touched).

### Strings to translate in `app/settings/page.tsx`

`OPTIONS` array (labels + descriptions):
| Line | English | Russian |
|---|---|---|
| 8 | `Off` / `Feedback does not affect ranking.` | `Выкл.` / `Отзывы не влияют на ранжирование.` |
| 9 | `Low` / `Subtle nudges from your votes.` | `Низкое` / `Едва заметное влияние ваших оценок.` |
| 10 | `Medium` / `Balanced personalization (default).` | `Среднее` / `Сбалансированная персонализация (по умолчанию).` |
| 11 | `High` / `Strong influence from your votes.` | `Высокое` / `Сильное влияние ваших оценок.` |

Toasts (lines 32–33):
- `Settings saved` → `Настройки сохранены`
- `Failed to save` → `Не удалось сохранить`

Page body:
- L39 `Settings` → `Настройки`
- L40 `Tune how your feedback affects analysis.` → `Настройте, как ваши отзывы влияют на анализ.`
- L44 `Feedback Influence` → `Влияние отзывов`
- L45–47 `How strongly your 👍 / 👎 votes re-rank future results. Rule-based and explainable — no machine learning.` → `Насколько сильно ваши оценки 👍 / 👎 меняют ранжирование будущих результатов. На основе правил и с понятной логикой — без машинного обучения.`
- L73 `How it works` → `Как это работает`
- L76 `Source affinity` → `Привязка к источнику`
- L76–78 `— sources you often mark Relevant get a score boost; Not Relevant gets a penalty.` → `— источники, которые вы часто отмечаете как «Релевантно», получают прибавку к оценке; «Не релевантно» — штраф.`
- L80 `Topic affinity` → `Привязка к темам`
- L80–82 `— categories you mark relevant get a small boost.` → `— категории, которые вы отмечаете как релевантные, получают небольшую прибавку.`
- L84 `Missed But Relevant` → `Пропущено, но релевантно`
- L84–86 `— a strong positive signal for that source and topics.` → `— сильный положительный сигнал для этого источника и тем.`

### What stays unchanged

- The `FeedbackInfluence` IDs (`"off"`/`"low"`/`"medium"`/`"high"`) — these are stored values/keys, only the display `label`/`desc` change.
- All JSX structure, classNames, emoji, and logic.
- All API routes (including `app/api/settings/route.ts`).

### Note on terminology

The feedback page (`app/feedback/page.tsx`) currently still shows the relevance terms in English (`Relevant` / `Not Relevant` / `Missed But Relevant`), so there is no existing Russian glossary to match. I've used natural Russian renderings above. If you'd prefer the Settings page to mirror the feedback page exactly, those three relevance terms could be left in English — but full translation is the more consistent choice for this task.

### Verification

After editing, run `npm run lint`/`tsc` (or the project's build) to confirm no syntax/JSX breakage. No behavior changes expected.

---

Since the mode is **plan_only**, I'm stopping here without modifying any files. Would you like me to proceed with the implementation (translating `app/settings/page.tsx`), or adjust any of the proposed Russian wording first?

