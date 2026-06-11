# Approved Plan

I now have everything I need. The prior translation tasks (Dashboard, Hero, NavBar) establish a clear pattern: translate only the user-facing UI strings in the page/component `.tsx` to **Russian**, leaving API routes, logic, and data untouched.

## Implementation Plan — Task 005: Translate Settings page

### Scope decision
The affected-files list includes 12 API route files, but the actual deliverable is translating the **Settings page UI**. Following the established pattern (Task 004 touched only `app/dashboard/page.tsx`, not the dashboard API route), the API routes are user-invisible — they return data/JSON error strings, not rendered UI. Translating them would change API behavior and contracts, which violates "smallest safe change" and "do not modify auth... unless explicitly required."

**Therefore: only `app/settings/page.tsx` will be edited.** The other 11 API files (auth/login, auth/logout, settings, analyze, benchmark, favorites, feedback, health, jobs) will **not** be modified.

### File to modify: `app/settings/page.tsx`

Translate these literal UI strings to Russian (no markup, class, prop, or logic changes):

**`OPTIONS` array (lines 8–11)** — labels + descriptions:
- `Off` → `Выкл.` / `Feedback does not affect ranking.` → `Отзывы не влияют на ранжирование.`
- `Low` → `Низкая` / `Subtle nudges from your votes.` → `Лёгкое влияние ваших оценок.`
- `Medium` → `Средняя` / `Balanced personalization (default).` → `Сбалансированная персонализация (по умолчанию).`
- `High` → `Высокая` / `Strong influence from your votes.` → `Сильное влияние ваших оценок.`

**Toast messages (lines 32–33):**
- `Settings saved` → `Настройки сохранены`
- `Failed to save` → `Не удалось сохранить`

**Header (lines 39–40):**
- `Settings` → `Настройки`
- `Tune how your feedback affects analysis.` → `Настройте, как ваши отзывы влияют на анализ.`

**Feedback Influence section (lines 44–47):**
- `Feedback Influence` → `Влияние отзывов`
- `How strongly your 👍 / 👎 votes re-rank future results. Rule-based and explainable — no machine learning.` → `Насколько сильно ваши 👍 / 👎 переранжируют будущие результаты. Основано на правилах и объяснимо — без машинного обучения.`

**How it works section (lines 73–86):**
- `How it works` → `Как это работает`
- `Source affinity` → `Сходство источников` / rest of li → `— источники, которые вы часто отмечаете как «Релевантно», получают прибавку к рейтингу; «Не релевантно» — штраф.`
- `Topic affinity` → `Сходство тем` / `— categories you mark relevant get a small boost.` → `— категории, которые вы отмечаете релевантными, получают небольшую прибавку.`
- `Missed But Relevant` → `Пропущено, но релевантно` / `— a strong positive signal for that source and topics.` → `— сильный положительный сигнал для этого источника и тем.`

### What stays unchanged
- All `FeedbackInfluence` IDs (`"off"`, `"low"`, `"medium"`, `"high"`) — these are API contract values consumed by `app/api/settings/route.ts` (`INFLUENCES` array). **Translating these would break persistence.**
- `fetch` calls, state logic, `className`, the `ru-RU` toast, imports.
- All API route files.

### Verification
- Visual/string-only change; no type or behavior impact.
- Optional: `npm run build` / lint to confirm no syntax breakage.

### Commit
Single commit matching convention: `Epic task: Task 005 — Translate Settings page`.

This is a single-file, string-only, fully reversible change. No files have been modified — stopping here per plan-only mode.

