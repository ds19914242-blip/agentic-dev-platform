I have enough context. The established pattern (Tasks 003/004) is translating user-facing English UI strings to Russian. The settings page is the only file with such strings; the API routes have no user-facing copy.

# Implementation Plan

## Summary

Translate all user-facing English strings in the Settings page (`app/settings/page.tsx`) to Russian, following the exact pattern established in Task 004 (Dashboard) and Task 003 (Hero). This includes the `OPTIONS` array labels/descriptions, page heading and subtitle, both section headings (`Feedback Influence`, `How it works`), the explanatory paragraph, the toast messages, and the "How it works" bullet list. No logic, types, or API behavior changes. The listed API routes contain no user-facing copy and require no edits.

## Files To Inspect

- `app/settings/page.tsx` — the only file with user-facing strings (already reviewed).
- `app/api/settings/route.ts` — confirm it returns no user-facing message strings (it serves `feedbackInfluence` JSON only; expected no change).
- `lib/storage/types.ts` — confirm `FeedbackInfluence` is a typed union (`off|low|medium|high`); option `id` values are keys and **must not** be translated.

## Implementation Steps

1. **`OPTIONS` array (lines 7–12):** translate only `label` and `desc`; keep `id` values (`off/low/medium/high`) unchanged.
   - `Off` → `Выкл`, desc → `Отзывы не влияют на ранжирование.`
   - `Low` → `Низкое`, desc → `Лёгкая корректировка по вашим оценкам.`
   - `Medium` → `Среднее`, desc → `Сбалансированная персонализация (по умолчанию).`
   - `High` → `Высокое`, desc → `Сильное влияние ваших оценок.`
2. **Page header (lines 39–40):** `Settings` → `Настройки`; subtitle → `Настройте, как ваши отзывы влияют на анализ.`
3. **Feedback section (lines 44–48):** heading `Feedback Influence` → `Влияние отзывов`; paragraph → Russian equivalent of "How strongly your 👍 / 👎 votes re-rank future results. Rule-based and explainable — no machine learning." (keep emojis).
4. **Toast messages (lines 32–33):** `Settings saved` → `Настройки сохранены`; `Failed to save` → `Не удалось сохранить` (keep `"success"`/`"error"` severity args unchanged).
5. **"How it works" section (lines 73–87):** heading → `Как это работает`; translate the three bullet emphasis terms and their descriptions (`Source affinity` → `Сходство источников`, `Topic affinity` → `Сходство тем`, `Missed But Relevant` → `Пропущено, но релевантно`), keeping the colored `<span>` markup intact.
6. Preserve all JSX structure, className strings, the `"ru-RU"` locale usage, and component logic exactly.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) — ensure no type errors from the `OPTIONS` literal edits.
- `npm run lint` if configured.
- Visual/manual check of `/settings`: option cards render, selecting one shows the success toast, descriptions display correctly.
- Grep the file for residual English UI strings to confirm full coverage.

## Risks

- **Low overall.** Main risk is accidentally translating `OPTIONS[].id` values, which are typed `FeedbackInfluence` keys persisted via the API — translating them would break saving/loading. Translate `label`/`desc` only.
- Ensure UTF-8 Cyrillic + emoji are preserved on save (consistent with prior tasks).
- Scope creep: the 11 listed API routes have no user-facing copy; editing them is unnecessary and out of scope for this translation task.
