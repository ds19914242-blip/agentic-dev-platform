# Claude Response

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

