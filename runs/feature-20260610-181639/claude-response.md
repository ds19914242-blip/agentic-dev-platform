# Claude Response

I have everything I need. Note that the **Affected Files list (API routes) is a red herring** — none of those files contain layout metadata or Footer text. The actual files for this task are `app/layout.tsx` and `components/Footer.tsx`. I'll flag this in the plan and base the work on the real targets, following the Russian-translation pattern established in Task 001.

---

# Implementation Plan — Task 002: Translate layout metadata and Footer

## Context & discrepancy

- The repo is being incrementally localized to Russian (`<html lang="ru">` already set; Task 001 translated `NavBar` links; reports page already translated).
- **The "Affected Files" list in the task (all `app/api/**` route handlers) does not match the task title.** API routes contain no layout metadata or Footer UI text. The genuinely relevant files are:
  - `app/layout.tsx` — exports `metadata` (title + description)
  - `components/Footer.tsx` — footer UI
- I will implement against the real targets and leave the API routes untouched.

## Strings to translate

### 1. `app/layout.tsx` (lines 14–18) — `metadata`
Keep the **brand name "RSS Agent Lab"** (proper noun, consistent with Footer); translate the descriptor and description.

| Field | Current | Proposed (RU) |
|---|---|---|
| `title` | `"RSS Agent Lab — Market Intelligence"` | `"RSS Agent Lab — Анализ рынка"` |
| `description` | `"Turn raw news feeds into a cited TOP-N market intelligence briefing."` | `"Превращайте новостные ленты в аналитическую сводку TOP-N по рынку со ссылками на источники."` |

Note: `subsets` already includes `"cyrillic"` (line 9), so Cyrillic glyphs render correctly — no font change needed.

### 2. `components/Footer.tsx`
Almost all footer content is dynamic/brand and should **not** be translated:
- `RSS Agent Lab v{APP_VERSION}` — brand + version → **keep**
- `{APP_ENV}` — runtime value (`production`/`development`) → **keep**

The only translatable literal:
| Line | Current | Proposed (RU) |
|---|---|---|
| 20 | `build {BUILD_TIME}` | `сборка {BUILD_TIME}` |

## Steps
1. Edit `app/layout.tsx`: replace `title` and `description` string values (lines 15–17).
2. Edit `components/Footer.tsx`: change the literal `build` → `сборка` (line 20), preserving the `{BUILD_TIME}` interpolation.
3. Verify build/typecheck still passes (e.g. `npm run build` or `next lint`/`tsc`), since these are string-only changes there is no functional risk.

## Scope & safety
- **No** changes to auth, billing, secrets, DB schema, deployment config, or any API route.
- Changes are string-literal only, fully reversible, isolated to two presentational files.
- Brand name, version, environment badge, and interpolated values are preserved exactly.

## Open question (minor)
- Whether to keep `"RSS Agent Lab"` untranslated in the title. I recommend keeping it (it's the product brand and is already kept untranslated in the Footer). If you'd prefer a fully Russian title with no brand token, say so and I'll adjust.

---

This is plan-only mode, so I've made **no file changes**. Ready to implement on your go-ahead.

