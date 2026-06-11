# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Epic task: Task 017 — Finish Profiles page remaining English labels

## Planner Input

I now have a clear picture of the remaining English text. Here is the implementation plan.

# Implementation Plan

## Summary

The Profiles page (`app/profiles/page.tsx`) is mostly translated to Russian, but a handful of UI labels remain in English. This task finishes the translation of all **visible** Russian-facing UI text on the Profiles page, plus the built-in profile content that the page renders. Following the established pattern in this repo (prior commits translated only visible UI strings, leaving code identifiers, enum values, and domain terms intact), the change is limited to user-facing display strings. The listed API routes contain only JSON `error` messages that are not surfaced in the Profiles UI today, so they are a lower-priority, optional cleanup.

## Files To Inspect

- `app/profiles/page.tsx` — primary file; contains the remaining English labels.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` strings rendered on the page (lines 117, 124).
- `src/analysis/performance.ts` — confirms mode enum values (`fast`/`balanced`/`deep`) are code identifiers that must stay; only their display labels get translated.
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — confirm topic chips are domain terms; decide whether they're in scope (likely left as-is, matching prior tasks).
- `app/api/profiles/route.ts` & `app/api/profiles/[id]/route.ts` — JSON error strings (`"Profile not found."`, `"Built-in profiles cannot be edited."`, etc.); verify whether any reach the UI before touching.

## Implementation Steps

1. **`app/profiles/page.tsx` — visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders the raw enum — map to a Russian display label (Быстрый/Сбалансированный/Глубокий) via a small lookup, leaving the stored value unchanged.
   - Line 192: `Include keywords` → `Ключевые слова (включить)`.
   - Line 206: `Exclude keywords` → `Ключевые слова (исключить)`.
   - Lines 234–236: select option labels `Fast`/`Balanced`/`Deep` → `Быстрый`/`Сбалансированный`/`Глубокий`. **Keep `value="fast|balanced|deep"` unchanged** — only the display text changes.
   - (Optional) Line 168/174 placeholders already Russian; confirm no stragglers.

2. **`src/analysis/profiles.ts` — built-in profile copy:**
   - Translate each `description` sentence to Russian (6 profiles, lines 11, 22, 33, 44, 55, 66).
   - Decide on `name` fields (e.g. "AI Security", "Vendor Radar"): translate or keep as domain brand-style terms. Recommend translating to match the fully-Russian UI unless prior tasks kept such names English. **Do not change `id` values.**
   - Leave `selectedTopics`, `includeKeywords`, `excludeKeywords` as-is (functional matching data).

3. **(Optional, lower priority) API error strings:** Only if confirmed user-facing — the Profiles page currently shows generic Russian toasts and does not display API `error` text, so translating these is cosmetic. If included for the broader epic, translate the `error`/`message` strings in `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts`, and the other listed routes, without altering status codes or response shapes.

## Validation Steps

- Run the type checker / build: `npm run build` (or `tsc --noEmit`) to confirm no breakage from the mode-label lookup or edits.
- Run lint: `npm run lint` if configured.
- Manually load `/profiles`: verify list (badge, mode label, built-in names/descriptions), editor (keyword labels, mode dropdown, buttons) all read in Russian.
- Confirm create/edit/delete still work — i.e. `defaultMode` values still persist as `fast`/`balanced`/`deep` and topic chips still toggle correctly (enum/identifier values untouched).

## Risks

- **Changing enum/identifier values instead of display text** — the highest risk. `defaultMode` option `value`s and `ALL_TOPICS` keys feed analysis logic a

## plan

I now have a clear picture of the remaining English text. Here is the implementation plan.

# Implementation Plan

## Summary

The Profiles page (`app/profiles/page.tsx`) is mostly translated to Russian, but a handful of UI labels remain in English. This task finishes the translation of all **visible** Russian-facing UI text on the Profiles page, plus the built-in profile content that the page renders. Following the established pattern in this repo (prior commits translated only visible UI strings, leaving code identifiers, enum values, and domain terms intact), the change is limited to user-facing display strings. The listed API routes contain only JSON `error` messages that are not surfaced in the Profiles UI today, so they are a lower-priority, optional cleanup.

## Files To Inspect

- `app/profiles/page.tsx` — primary file; contains the remaining English labels.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` strings rendered on the page (lines 117, 124).
- `src/analysis/performance.ts` — confirms mode enum values (`fast`/`balanced`/`deep`) are code identifiers that must stay; only their display labels get translated.
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — confirm topic chips are domain terms; decide whether they're in scope (likely left as-is, matching prior tasks).
- `app/api/profiles/route.ts` & `app/api/profiles/[id]/route.ts` — JSON error strings (`"Profile not found."`, `"Built-in profiles cannot be edited."`, etc.); verify whether any reach the UI before touching.

## Implementation Steps

1. **`app/profiles/page.tsx` — visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders the raw enum — map to a Russian display label (Быстрый/Сбалансированный/Глубокий) via a small lookup, leaving the stored value unchanged.
   - Line 192: `Include keywords` → `Ключевые слова (включить)`.
   - Line 206: `Exclude keywords` → `Ключевые слова (исключить)`.
   - Lines 234–236: select option labels `Fast`/`Balanced`/`Deep` → `Быстрый`/`Сбалансированный`/`Глубокий`. **Keep `value="fast|balanced|deep"` unchanged** — only the display text changes.
   - (Optional) Line 168/174 placeholders already Russian; confirm no stragglers.

2. **`src/analysis/profiles.ts` — built-in profile copy:**
   - Translate each `description` sentence to Russian (6 profiles, lines 11, 22, 33, 44, 55, 66).
   - Decide on `name` fields (e.g. "AI Security", "Vendor Radar"): translate or keep as domain brand-style terms. Recommend translating to match the fully-Russian UI unless prior tasks kept such names English. **Do not change `id` values.**
   - Leave `selectedTopics`, `includeKeywords`, `excludeKeywords` as-is (functional matching data).

3. **(Optional, lower priority) API error strings:** Only if confirmed user-facing — the Profiles page currently shows generic Russian toasts and does not display API `error` text, so translating these is cosmetic. If included for the broader epic, translate the `error`/`message` strings in `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts`, and the other listed routes, without altering status codes or response shapes.

## Validation Steps

- Run the type checker / build: `npm run build` (or `tsc --noEmit`) to confirm no breakage from the mode-label lookup or edits.
- Run lint: `npm run lint` if configured.
- Manually load `/profiles`: verify list (badge, mode label, built-in names/descriptions), editor (keyword labels, mode dropdown, buttons) all read in Russian.
- Confirm create/edit/delete still work — i.e. `defaultMode` values still persist as `fast`/`balanced`/`deep` and topic chips still toggle correctly (enum/identifier values untouched).

## Risks

- **Changing enum/identifier values instead of display text** — the highest risk. `defaultMode` option `value`s and `ALL_TOPICS` keys feed analysis logic and storage; translating these would break profile saving and matching. Translate only display strings.
- **Built-in profile `id` c

## qa_plan

# QA Plan

## Feature Request

Epic task: Task 017 — Finish Profiles page remaining English labels

## Based On Plan

I now have a clear picture of the remaining English text. Here is the implementation plan.

# Implementation Plan

## Summary

The Profiles page (`app/profiles/page.tsx`) is mostly translated to Russian, but a handful of UI labels remain in English. This task finishes the translation of all **visible** Russian-facing UI text on the Profiles page, plus the built-in profile content that the page renders. Following the established pattern in this repo (prior commits translated only visible UI strings, leaving code identifiers, enum values, and domain terms intact), the change is limited to user-facing display strings. The listed API routes contain only JSON `error` messages that are not surfaced in the Profiles UI today, so they are a lower-priority, optional cleanup.

## Files To Inspect

- `app/profiles/page.tsx` — primary file; contains the remaining English labels.
- `src/analysis/profiles.ts` — built-in profile `name`/`description` strings rendered on the page (lines 117, 124).
- `src/analysis/performance.ts` — confirms mode enum values (`fast`/`balanced`/`deep`) are code identifiers that must stay; only their display labels get translated.
- `src/analysis/criteria.ts` (`ALL_TOPICS`) — confirm topic chips are domain terms; decide whether they're in scope (likely left as-is, matching prior tasks).
- `app/api/profiles/route.ts` & `app/api/profiles/[id]/route.ts` — JSON error strings (`"Profile not found."`, `"Built-in profiles cannot be edited."`, etc.); verify whether any reach the UI before touching.

## Implementation Steps

1. **`app/profiles/page.tsx` — visible labels:**
   - Line 121: `built-in` badge → `встроенный`.
   - Line 136: `{p.defaultMode}` renders the raw enum — map to a Russian display label (Быстрый/Сбалансированный/Глубокий) via a small lookup, leaving the stored value unchanged.
   - Line 192: `Include keywords` → `Ключевые слова (включить)`.
   - Line 206: `Exclude keywords` → `Ключевые слова (исключить)`.
   - Lines 234–236: select option labels `Fast`/`Balanced`/`Deep` → `Быстрый`/`Сбалансированный`/`Глубокий`. **Keep `value="fast|balanced|deep"` unchanged** — only the display text changes.
   - (Optional) Line 168/174 placeholders already Russian; confirm no stragglers.

2. **`src/analysis/profiles.ts` — built-in profile copy:**
   - Translate each `description` sentence to Russian (6 profiles, lines 11, 22, 33, 44, 55, 66).
   - Decide on `name` fields (e.g. "AI Security", "Vendor Radar"): translate or keep as domain brand-style terms. Recommend translating to match the fully-Russian UI unless prior tasks kept such names English. **Do not change `id` values.**
   - Leave `selectedTopics`, `includeKeywords`, `excludeKeywords` as-is (functional matching data).

3. **(Optional, lower priority) API error strings:** Only if confirmed user-facing — the Profiles page currently shows generic Russian toasts and does not display API `error` text, so translating these is cosmetic. If included for the broader epic, translate the `error`/`message` strings in `app/api/profiles/route.ts`, `app/api/profiles/[id]/route.ts`, and the other listed routes, without altering status codes or response shapes.

## Validation Steps

- Run the type checker / build: `npm run build` (or `tsc --noEmit`) to confirm no breakage from the mode-label lookup or edits.
- Run lint: `npm run lint` if configured.
- Manually load `/profiles`: verify list (badge, mode label, built-in names/descriptions), editor (keyword labels, mode dropdown, buttons) all read in Russian.
- Confirm create/edit/delete still work — i.e. `defaultMode` values still persist as `fast`/`balanced`/`deep` and topic chips still toggle correctly (enum/identifier values untouched).

## Risks

- **Changing enum/identifier values instead of display text** — the highest risk. `defaultMode` option `value`s and `ALL_TOPICS` keys feed analysis logic and storage; 
