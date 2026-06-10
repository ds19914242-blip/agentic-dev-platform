# Claude Response

I now have a complete picture of the flow. Here's my analysis and plan.

---

## What already exists

**Article model & source signal.** Every article (`RssTextArticle`, `src/types/report.ts:9`) carries a `link`. There is no explicit "source/domain" field — the **hostname of `link` is the de-facto source**. Two places already derive it independently:
- `src/reporting/transparency.ts:89` — `hostnameOf(link)` → strips `www.`, falls back to `"неизвестно"`. Used for `sourceDistribution`.
- `src/analysis/feedbackRanking.ts:34` — `hostOf(link)` → strips `www.`, falls back to `""`. Used for per-source feedback affinity.

**Criteria flow.** `AnalysisCriteria` (`src/analysis/criteria.ts`) holds `selectedTopics / includeKeywords / excludeKeywords / topN / performanceMode`. It flows:
`POST /api/analyze` → `normalizeCriteria()` → `startAnalysis()` → `runTopNewsReport()` → `prefilterArticles()` + the LLM agents. `resolveKeywords()` turns topics+keywords into effective include/exclude lists.

**The pipeline** (`customerTopNewsWorkflow.ts → runTopNewsReport`): parse → **deterministic keyword prefilter** (`prefilterArticles`) → cached LLM batch analysis → rank → TOP-N select/backfill → trends/conclusion → deterministic transparency stats. Filtering today is purely **keyword-based**; there is no domain/source filter anywhere.

**About the "affected files" list.** Most of the listed files are **not the right place** for this feature:
- `criteriaBatchAgent.ts`, `summaryBatchAgent.ts`, `trendAnalysisAgent.ts` — LLM agents; domain filtering is a deterministic, pre-LLM concern and should not touch prompts.
- `feedbackRanking.ts`, `performance.ts`, `profiles.ts`, `llm/client.ts` — unrelated to a per-run domain filter.

The honest, minimal implementation lives in **`criteria.ts`** (the only listed file that genuinely changes) plus two wiring points not in the list but required: the **workflow** and the **API route**.

---

## Implementation plan

Domain filtering as a **deterministic allow/deny list on `link` hostname**, applied once right after parse and before the keyword prefilter. Mirrors the existing `includeKeywords/excludeKeywords` shape so it's predictable and reversible.

**1. `src/analysis/criteria.ts` (core — the one in-scope file)**
- Extend `AnalysisCriteria` with two optional fields:
  ```ts
  includeDomains?: string[]; // whitelist: if non-empty, keep only these hosts
  excludeDomains?: string[]; // blacklist: drop these hosts
  ```
- Add a shared `hostnameOf(link)` helper (same `www.`-stripping logic already duplicated in transparency.ts / feedbackRanking.ts) and a pure `filterByDomain(articles, criteria)` that:
  - normalizes each domain entry (lowercase, strip `www.`/scheme/path),
  - keeps an article if (`includeDomains` empty **or** host suffix-matches an entry) **and** host does not suffix-match any `excludeDomains` entry. Suffix match so `example.com` covers `sub.example.com`.
  - articles with an unparseable link → excluded only when a whitelist is active (treated as `"неизвестно"`).
- Update `normalizeCriteria()` to parse both arrays (default `[]`).
- `DEFAULT_CRITERIA` stays unchanged (no `*Domains` → empty → **no behavioral change** for CLI / existing callers).

**2. `src/workflows/customerTopNewsWorkflow.ts` (integration point)**
- In `runTopNewsReport`, immediately after parse and before `prefilterArticles`, apply `filterByDomain(articles, criteria)`.
- Feed the domain-dropped articles into the existing `dropped`/exclusion accounting so transparency stats stay accurate (add them to `excludedArticles`), and add a `console.log` + `onProgress` line (e.g. "После фильтра источников: N"). Update `removedByPrefilter` semantics or add the count to the existing dropped pool — keep it auditable.
- Guard: if a whitelist filters everything out, fall back gracefully (same spirit as the existing "never send an empty candidate set" guard) or surface a clear error rather than a silent empty report.

**3. `app/api/analyze/route.ts` (web wiring)**
- Accept `includeDomains?: string[]` and `excludeDomains?: string[]` in the request body and pass them into `normalizeCriteria(...)`. No other route changes.

**4. (Optional, flag for follow-up — not in this change)**
- UI input in `components/TopicSelector.tsx` / `app/page.tsx` for entering domains.
- Persisting domains on `RunRecord` (`lib/storage/types.ts`) and `Profile` (`profiles.ts`). I'd **defer** these to keep the change small; the backend accepts and applies domains regardless.

**5. Verify**
- `npx tsc --noEmit`.
- Targeted check: a criteria with `excludeDomains:["example.com"]` drops those articles pre-LLM; `includeDomains:["a.com","b.com"]` keeps only those; empty arrays reproduce current output byte-for-byte.

---

## Summary of changed files

| File | Change | Risk |
|------|--------|------|
| `src/analysis/criteria.ts` | Add `includeDomains`/`excludeDomains`, `hostnameOf` + `filterByDomain` helpers, normalize parsing | Low — additive, optional fields, defaults preserve behavior |
| `src/workflows/customerTopNewsWorkflow.ts` | Apply `filterByDomain` after parse; fold dropped into exclusion stats | Medium — touches the live pipeline; needs the empty-whitelist guard |
| `app/api/analyze/route.ts` | Accept + forward domain arrays | Low — additive request fields |

**Not touched** (and why): the three LLM agents, `feedbackRanking.ts`, `performance.ts`, `profiles.ts`, `llm/client.ts` — domain filtering is deterministic and pre-LLM, so these need no changes despite appearing in the affected-files list. No auth, billing, secrets, DB schema, or deployment config touched.

## Risks & mitigations
- **Over-filtering** (aggressive whitelist → empty report): add a guard/fallback mirroring the existing empty-candidate-set safeguard.
- **Stat accuracy**: domain-dropped articles must enter the exclusion accounting, or `totalFound` vs funnel counts won't reconcile. Handled in step 2.
- **Host-matching edge cases**: unparseable links, subdomains, `www.` — reuse the already-proven `www.`-stripping logic and use suffix matching.
- **Duplication**: `hostnameOf` exists twice already; introducing a shared helper is good but I'll keep the existing two call sites untouched in this change to stay minimal (note as a possible later refactor).

This plan is ready to implement on your go-ahead — I've made no file changes yet.

