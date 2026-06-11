# Architecture Review

## Feature Request

Epic task: Task 005 — Translate Settings page

## Planner Input

## Files inspected

The only file with visible Settings UI text is `app/settings/page.tsx`. The API route (`app/api/settings/route.ts`) contains one non-user-facing error string (`"Invalid JSON."`) returned to API callers, not rendered in the UI. The other listed API routes contain no Settings-page UI text.

# Implementation Plan

## Summary

Translate the visible UI text of the Settings page to Russian, matching the established project convention (Task 001/earlier epics) of changing only user-facing strings in the page component while leaving code, identifiers, API contracts, and stored values (`off`/`low`/`medium`/`high`) untouched.

## Files To Inspect

- `app/settings/page.tsx` — primary file; all visible strings live here (page title/subtitle, the `OPTIONS` `label`/`desc` fields, the two section headings + descriptions, the "How it works" list, and the two `toast(...)` messages).
- `app/api/settings/route.ts` — confirm the `feedbackInfluence` value contract (`off/low/medium/high`) must not change; its `"Invalid JSON."` string is an API error, not Settings UI — leave as-is to stay consistent with prior tasks scoping changes to rendered page text.

## Implementation Steps

1. In `app/settings/page.tsx`, translate the `OPTIONS` array's human-readable fields only:
   - `label`: Off → «Выкл.», Low → «Низкое», Medium → «Среднее», High → «Высокое».
   - `desc`: translate each description (e.g. "Feedback does not affect ranking." → «Отзывы не влияют на ранжирование.», "Balanced personalization (default)." → «Сбалансированная персонализация (по умолчанию).», etc.).
   - Keep each `id` (`off`/`low`/`medium`/`high`) unchanged — these are the API/storage values.
2. Translate the header block (lines 39–40): "Settings" → «Настройки»; subtitle "Tune how your feedback affects analysis." → Russian.
3. Translate the "Feedback Influence" section (lines 44–48): heading and the descriptive paragraph (including the "Rule-based and explainable — no machine learning" note); keep the 👍/👎 emojis.
4. Translate the "How it works" section (lines 73–87): heading plus the three list items, including the colored emphasis spans ("Source affinity", "Topic affinity", "Missed But Relevant") and their explanatory text — translate the visible words but keep the surrounding JSX/`className` markup intact.
5. Translate the toast messages (lines 32–33): "Settings saved" → «Настройки сохранены», "Failed to save" → «Не удалось сохранить»; keep the `"success"`/`"error"` type args unchanged.
6. Leave all imports, types (`FeedbackInfluence`), hooks, fetch paths, and JSX structure unchanged.

## Validation Steps

- `npx tsc --noEmit` (or project typecheck) to confirm no type/JSX breakage.
- `npm run lint` if configured.
- Run the app, navigate to `/settings`, and verify: title/subtitle, all four influence cards, both section bodies, and the save/fail toasts render in Russian; clicking an option still saves (PATCH succeeds, success toast shows).
- Confirm selecting an option still persists by reloading — the API still receives the unchanged `off/low/medium/high` values.

## Risks

- **Scope creep into API strings**: changing `"Invalid JSON."` or the `INFLUENCES` values would alter the API contract; keep changes confined to rendered UI text per prior-task convention.
- **Accidentally translating an `id` value** in `OPTIONS`, which would break save/highlight logic (`influence === o.id`) and the stored setting.
- **JSX/emphasis spans**: translating inside the colored `<span>` elements risks disturbing markup — edit only the text nodes.
- **Encoding**: ensure Cyrillic is saved as UTF-8 (default) to avoid mojibake.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- API route: app/api/settings/route.ts
- Other: app/settings/page.tsx
- API route: app/api/analyze/route.ts
- API route: app/api/auth/login/route.ts
- API route: app/api/auth/logout/route.ts
- API route: app/api/benchmark/route.ts
- API route: app/api/favorites/[id]/route.ts
- API route: app/api/favorites/route.ts
- API route: app/api/feedback/route.ts
- API route: app/api/health/db/route.ts
- API route: app/api/health/route.ts
- API route: app/api/jobs/[jobId]/route.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.
