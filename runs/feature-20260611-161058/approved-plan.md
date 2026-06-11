# Approved Plan

I have enough to write the plan. Here's what I found.

## Findings

**The active progress view is `components/ProgressTimeline.tsx`**, rendered in `app/page.tsx:293` when `phase === "running"`. It is already ~95% Russian (`Парсинг`, `Префильтр`, `LLM-анализ`, `Тренды`, `Готово`, `Прошло`, `Из кэша`, `Ожидание логов…`, etc.). The **one remaining English string** is the header eyebrow:

```
components/ProgressTimeline.tsx:48    <span className="eyebrow">Analyzing</span>
```

That is the "Analyzing" header the task targets.

**Everything else feeding the progress view is already translated:**
- Status/step/log strings come from `lib/jobStore.ts` (`В очереди…`, `Парсинг файла…`, `Старт анализа`, `Готово`, `Анализ завершён`, `Ошибка:…`) — already Russian.
- `components/ProgressView.tsx` (an alternate, **unused** component — not imported anywhere) is also already fully Russian.

## ⚠️ Discrepancy with the "Affected Files" list

The listed affected files do **not** contain any progress-view header:
- `src/util/progress.ts` is a **CLI/terminal** progress reporter (`batches`, `Elapsed`, `ETA`, `Average`, `sec/batch`) — developer-facing stdout, not a web "progress view." Prior epic tasks (commits) scoped strictly to *visible web UI text*.
- The API routes (`analyze`, `auth/*`, `benchmark`, `favorites`, `feedback`, `health/*`, `jobs`, `overview`) return JSON status/error payloads. `overview` and `jobs` have no user-facing English; the others contain English *error* strings, but those are not "progress views / Analyzing headers."

The file that actually holds the "Analyzing" header — `components/ProgressTimeline.tsx` — is **not** in the affected-files list. I'm treating the task title as authoritative and the file list as imprecise auto-detection. Flagging this rather than silently translating the unrelated CLI/error strings.

## Implementation Plan (smallest safe change)

**Single edit — `components/ProgressTimeline.tsx`, line 48:**

```diff
-          <span className="eyebrow">Analyzing</span>
+          <span className="eyebrow">Идёт анализ</span>
```

- **Recommended translation:** `Идёт анализ` (matches the present-progressive "currently analyzing" sense of the header). Acceptable alternatives: `Анализ` (terse, matches the noun-style step labels below it) or `Анализируем…`.
- No props, styling, logic, or layout change — pure text swap inside the existing `eyebrow` span.

**Out of scope (recommend not touching):**
- `src/util/progress.ts` — CLI output, not a web progress view; outside the "visible UI" pattern of this epic.
- API-route JSON error strings — not progress headers.
- `components/ProgressView.tsx` — unused and already Russian.

**Verification after the change:**
- `npm run build` / `tsc` (text-only change, should pass trivially).
- Optional manual: start an analysis run and confirm the header above the progress bar reads the Russian text while `phase === "running"`.

**Reversibility:** one-line revert.

---

This is a one-line, fully reversible change. Per the task I've stopped at the plan and made no modifications. Want me to proceed with the edit (recommended `Идёт анализ`), or would you prefer `Анализ` / `Анализируем…` instead?

