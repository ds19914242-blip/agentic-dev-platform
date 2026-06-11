# Review Implementation

Review whether the implementation satisfies the feature request.

Return ONLY valid JSON with this shape:

{
  "requirements_covered": true,
  "scope_creep": false,
  "architecture_risk": "low",
  "blocking_issues": [],
  "summary": ""
}

Rules:
- Be strict but practical.
- Do not invent issues.
- Mark requirements_covered=false only if the feature clearly was not implemented.
- Mark scope_creep=true if implementation changed unrelated areas.
- architecture_risk must be one of: low, medium, high.

# Feature Request

Добавить фильтрацию новостей по домену источника.

# Approved Plan

# Approved Plan

I asked because the choice changes the plan, but I'll proceed with the most direct interpretation and note the alternative. Here is the plan.

---

# Implementation Plan — Filter news by source domain

## Summary of findings

**What "news" are and where they render.** The user-facing news list is the report **Dashboard** (`components/Dashboard.tsx`), section "ТОП-N новостей" plus "Potentially Relevant". Each item is a `RankedArticle` (`src/types/report.ts`) rendered by `components/NewsCard.tsx`. The source domain is already derived there as `host = hostname(item.article.link)` (`NewsCard.tsx:9-15,50`) — `new URL(link).hostname` with `www.` stripped; Telegram items resolve to `t.me`.

**The "Affected Files" list is misleading.** Every file listed is an API route (`app/api/...`). None of them render or filter news items, and the feature needs no API/DB/schema change — the report data (`ReportData.topNews`) already contains each article's link, from which the domain is computed client-side. I am treating that list as auto-generated boilerplate and **not** modifying those routes. If the intent was actually a server-side/API filter, stop me — but there is no news-listing API endpoint that returns article items to filter (the report is loaded whole via `/api/runs/[id]`).

**Existing patterns to reuse:**
- `hostname()` helper already exists (duplicated) in `NewsCard.tsx`, `PreviewPanel.tsx`, `src/reporting/transparency.ts`, `feedbackRanking.ts`.
- Chip filter UI pattern already exists in `app/reading-list/page.tsx:48-58` (`chip` / `chip-on` / `chip-off` classes) — I'll match it.
- `Dashboard.tsx` is already a `"use client"` component, so local `useState` is available with no new wiring.

**Recommended scope:** add a client-side domain filter to the report Dashboard news section. This is the smallest, fully reversible change (one component, pure UI). The Reading List (`app/reading-list/page.tsx`) is a secondary candidate (it has a `source` field on `FavoriteArticle`); I've left it out to keep the change minimal — easy to add later with the same approach.

## Changes

### 1. `components/Dashboard.tsx` (primary change)

Add a client-side source-domain filter over the news lists.

- **Import** `useState`/`useMemo` from `react` (file is already `"use client"`).
- **Add a small `hostname()` helper** at the top of the file (mirror `NewsCard.tsx:9-15` exactly so behavior matches — `www.` stripped, empty string on parse failure). I'll keep it local rather than refactoring the 4 existing copies into a shared util, to keep the diff minimal and reversible. (Noted as optional follow-up below.)
- **Derive the domain list** with `useMemo` from `topNews` (the canonical selected list). For each item compute `hostname(item.article.link)`; bucket empty hostnames under a sentinel label (e.g. `"без источника"`). Produce a sorted, de-duplicated list of `{ domain, count }`.
- **Add state:** `const [domain, setDomain] = useState<string | null>(null)` (`null` = «Все источники»).
- **Render a chip row** directly under the `<h2>ТОП-N новостей</h2>` heading (Dashboard.tsx:116-119): an "Все" chip plus one chip per domain (showing `domain (count)`), using the existing `chip` / `chip-on` / `chip-off` classes. Only render the row when there are ≥2 distinct domains (a single-source report needs no filter).
- **Filter before mapping:** compute `visibleTopNews = domain ? topNews.filter(i => host(i)===domain) : topNews` and apply the same to `potentiallyRelevant`. 
- **Preserve original ranks:** the current code passes `rank={i + 1}` (Dashboard.tsx:127). To avoid renumbering filtered results misleadingly, compute each item's rank from its index in the *unfiltered* list, then filter. Concretely: map over `topNews` with original index → `{ item, rank: i+1 }`, then `.filter(domain match)`, then render. Same for `potentiallyRelevant` (its rank base stays `topNews.length + originalIndex + 1`). This keeps "#3" meaning the 3rd-ranked article regardless of filter.
- **Empty-filter state:** the existing `topNews.length === 0` empty card (Dashboard.tsx:120-123) should key off the *visible* count, with a filter-aware message (e.g. "Нет новостей для выбранного источника").
- **Charts/stats untouched:** the filter affects only the news card lists, not `sourceDistribution`/analytics (those remain full-report figures, which is correct).

No prop/signature changes to `Dashboard` or `NewsCard` — `NewsCard` still receives one `item` + `rank`.

## Out of scope (explicitly not touching)
- Any `app/api/**` route (incl. the 12 listed) — no server change needed.
- Auth, billing, secrets, DB schema, storage types, deployment config.
- `src/reporting/transparency.ts` source-distribution logic.

## Optional follow-ups (not in this change)
- Lift the duplicated `hostname()` into a shared `lib/hostname.ts` and update the 4 call sites — pure refactor, deferred to keep this diff small.
- Mirror the same domain filter on `app/reading-list/page.tsx` (uses `FavoriteArticle.source`, already a hostname) next to the existing All/Unread/Read chips.

## Verification
- `npm run build` / typecheck (TS) to confirm no type errors.
- Manual: open a saved report at `/run/[id]` with articles from ≥2 domains; confirm chips appear, selecting one narrows both the TOP and Potentially-Relevant grids, ranks stay stable, "Все" restores the full list, and a domain with no Potentially-Relevant items shows the empty-state message.

## Uncertainty flag
The only material ambiguity is **location** (report Dashboard vs. Reading List vs. both). I've planned for the report Dashboard as the primary news view; say the word if you want the Reading List included or instead.

No files have been modified. Stopping after the plan as requested.



# Implementation Response

# Claude Implementation Response

The chip classes exist. Implementation complete.

## Summary of changes

**`components/Dashboard.tsx`** (only file modified):
- Added `useMemo`/`useState` imports.
- Added a local `hostname()` helper mirroring `NewsCard.tsx` exactly (`www.` stripped, empty string on parse failure) plus a `NO_SOURCE` sentinel (`"без источника"`).
- Added `domain` filter state (`null` = all sources).
- Pre-computed `rankedTopNews`/`rankedPotential` that tag each article with its **unfiltered** 1-based rank, so `#N` stays stable when a filter is active.
- Derived a de-duplicated, ru-sorted `domains` list with per-domain counts from the canonical TOP list.
- Rendered a chip row (`Все источники` + one chip per `domain (count)`) under the "ТОП-N новостей" heading, only when ≥2 distinct domains exist, using the existing `chip`/`chip-on`/`chip-off` classes.
- Filtered both the TOP and Potentially-Relevant grids by the selected domain; both now show a filter-aware empty-state message ("Нет новостей для выбранного источника"), while the TOP grid keeps the original "проверьте формат файла" message when the report itself is empty.
- Charts/stats/analytics untouched — they remain full-report figures.

No prop/signature changes to `Dashboard` or `NewsCard`. No `app/api/**`, schema, or config changes.

## Verification
- `npx tsc --noEmit` → passes, no errors.
- Confirmed `chip`/`chip-on`/`chip-off` classes exist in `app/globals.css`.

## Risks
- **Low.** Pure client-side UI change in one component, fully reversible.
- **Hostname duplication:** the helper is a 5th copy of `hostname()`. Behavior matches `NewsCard` so filter chips and card labels stay consistent, but a future change to one copy must be mirrored. (Plan flagged a shared `lib/hostname.ts` as an optional follow-up.)
- **`key` change:** list keys switched from array index to `rank`. Ranks are unique within each list, so this is safe and actually more stable than index keys under filtering.
- **Manual UI not exercised:** I didn't run the app. Suggested manual check — open a saved report with articles from ≥2 domains and confirm chips appear, selection narrows both grids, ranks stay stable, and "Все источники" restores the full list.


# Validation Report

# Validation Result

## Overall Result

passed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build

  ▲ Next.js 14.2.35
  - Environments: .env

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
   Generating static pages (0/19) ...
   Generating static pages (4/19) 
   Generating static pages (9/19) 
   Generating static pages (14/19) 
 ✓ Generating static pages (19/19)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    6.38 kB         214 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ƒ /api/analyze                         0 B                0 B
├ ƒ /api/auth/login                      0 B                0 B
├ ƒ /api/auth/logout                     0 B                0 B
├ ƒ /api/benchmark                       0 B                0 B
├ ƒ /api/favorites                       0 B                0 B
├ ƒ /api/favorites/[id]                  0 B                0 B
├ ƒ /api/feedback                        0 B                0 B
├ ƒ /api/health                          0 B                0 B
├ ƒ /api/health/db                       0 B                0 B
├ ƒ /api/jobs/[jobId]                    0 B                0 B
├ ƒ /api/overview                        0 B                0 B
├ ƒ /api/profiles                        0 B                0 B
├ ƒ /api/profiles/[id]                   0 B                0 B
├ ƒ /api/report/[id]/docx                0 B                0 B
├ ƒ /api/report/[id]/json                0 B                0 B
├ ƒ /api/report/[id]/markdown            0 B                0 B
├ ƒ /api/report/[id]/pdf                 0 B                0 B
├ ƒ /api/rss/collect                     0 B                0 B
├ ƒ /api/rss/collections                 0 B                0 B
├ ƒ /api/rss/collections/[id]            0 B                0 B
├ ƒ /api/rss/sources                     0 B                0 B
├ ƒ /api/rss/sources/[id]                0 B                0 B
├ ƒ /api/rss/summarize                   0 B                0 B
├ ƒ /api/rss/test                        0 B                0 B
├ ƒ /api/runs                            0 B                0 B
├ ƒ /api/runs/[id]                       0 B                0 B
├ ƒ /api/settings                        0 B                0 B
├ ƒ /api/upload                          0 B                0 B
├ ○ /benchmark                           2.5 kB         92.6 kB
├ ○ /collections                         3.21 kB        90.5 kB
├ ○ /dashboard                           1.89 kB        97.9 kB
├ ○ /feedback                            1.66 kB          89 kB
├ ○ /history                             152 B          87.5 kB
├ ○ /login                               1.41 kB        88.7 kB
├ ○ /profiles                            3.3 kB         90.6 kB
├ ○ /reading-list                        1.8 kB         89.1 kB
├ ○ /reports                             2.63 kB        98.7 kB
├ ○ /rss                                 152 B          87.5 kB
├ ○ /rss/collections                     152 B          87.5 kB
├ ƒ /run/[id]                            936 B           215 kB
├ ○ /settings                            2.06 kB        89.4 kB
├ ○ /sources                             7.75 kB        95.1 kB
├ ○ /templates                           152 B          87.5 kB
└ ○ /workspace                           152 B          87.5 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/117-c2e8725fecde5126.js       31.7 kB
  ├ chunks/fd9d1056-307a36020502e7d7.js  53.6 kB
  └ other shared chunks (total)          1.95 kB


ƒ Middleware                             26.9 kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand


```

### STDERR

```text

```

