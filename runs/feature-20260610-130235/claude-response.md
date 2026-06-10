# Claude Response

## What already exists

**Data flow (the relevant path).** A `.txt` upload is parsed into `RssTextArticle[]` (each has `number`, `date`, `title`, `summary`, `link`). The workflow `runTopNewsReport` (`src/workflows/customerTopNewsWorkflow.ts`) then:

1. resolves `AnalysisCriteria` → include/exclude **keyword** lists via `resolveKeywords()`;
2. runs the deterministic **keyword** prefilter (`prefilterArticles`) to cut the feed to `maxCandidates`;
3. runs the cached LLM batch analysis (`criteriaBatchAgent`), ranks, selects TOP-N, backfills;
4. computes deterministic transparency stats.

**Criteria model.** `AnalysisCriteria` (`src/analysis/criteria.ts`) holds `selectedTopics`, `includeKeywords`, `excludeKeywords`, `topN`, `performanceMode`. It is normalized from the API body by `normalizeCriteria()` and threaded everywhere. `app/api/analyze/route.ts` builds it from the request body. Profiles (`src/analysis/profiles.ts`) and storage types mirror the same fields.

**Domain/host handling already present.** Hostname extraction is already implemented twice — `hostnameOf()` in `src/reporting/transparency.ts` (used for `sourceDistribution`) and `hostOf()` in `src/analysis/feedbackRanking.ts`. Both do `new URL(link).hostname.replace(/^www\./,"")`. So "source = link hostname" is the established, auditable convention. There is **no filtering by domain today** — domains are only counted for stats and used for feedback affinity.

**Cache keying.** `AnalysisCache.key()` (`lib/analysisCache.ts`) hashes article content + topics + include/exclude keywords + model. A per-article LLM verdict does not depend on which *other* articles were filtered out, so domain filtering does **not** require a cache-key change.

**Note on the provided "affected files" list.** Most listed files (`summaryBatchAgent`, `trendAnalysisAgent`, `feedbackRanking`, `performance`, `profiles`, `llm/client`) are *not* the right insertion points for this feature — they consume criteria or are unrelated layers. The real seams are `src/analysis/criteria.ts` (the data model) plus the prefilter/workflow (not in the list but required). I'll keep edits minimal and centered on the data model + one deterministic filter step.

## Implementation plan

The smallest, reversible design: domain filtering is a **deterministic pre-LLM step**, modeled exactly like the existing keyword include/exclude, keyed off `article.link` hostname.

**1. Extend the criteria model — `src/analysis/criteria.ts`**
- Add two optional fields to `AnalysisCriteria`:
  - `includeDomains?: string[]` — allowlist (if non-empty, keep only these hosts).
  - `excludeDomains?: string[]` — blocklist (drop these hosts).
- Both default to empty/undefined so existing behavior is byte-for-byte unchanged (CLI `DEFAULT_CRITERIA` leaves them empty).
- In `normalizeCriteria()`, coerce both to arrays (mirroring the `includeKeywords` handling), trimming/lowercasing entries and stripping a leading `www.`.

**2. Add a pure filter helper**
- New small function `filterByDomain(articles, criteria): { kept, droppedByDomain }`, placed in `src/analysis/criteria.ts` (or a tiny `src/analysis/domainFilter.ts`). Logic: normalize each `article.link` host (reuse the same `replace(/^www\./,"")` convention); drop if host ∈ `excludeDomains`, or if `includeDomains` non-empty and host ∉ it. Match on exact host plus suffix (`host === d || host.endsWith("." + d)`) so `example.com` also covers `news.example.com`.
- Optionally factor the duplicated hostname helper into one shared util and reuse it in `transparency.ts`/`feedbackRanking.ts` — *optional cleanup, can be skipped to stay minimal.*

**3. Apply it in the workflow — `src/workflows/customerTopNewsWorkflow.ts`**
- Right after parse, before `prefilterArticles`, run `filterByDomain(articles, criteria)`. Feed `kept` into the prefilter.
- Add `droppedByDomain` into the `excludedArticles`/`dropped` accounting so `processingStats.removedByPrefilter` (or a new honest counter) and `exclusionReasons` stay truthful. Keep the existing "never send empty candidate set" guard.

**4. Thread through the API — `app/api/analyze/route.ts`**
- Accept `includeDomains` / `excludeDomains` in the request body and pass them into `normalizeCriteria(...)`. (The route already forwards analogous keyword fields, so this is a 2-line addition.)

**5. (Optional, follow-up) UI + profiles/persistence**
- `TopicSelector`/`app/page.tsx` could expose a domain allow/block input, and `lib/storage/types.ts` + `profiles.ts` could persist the new fields. These are outside the listed analysis files and not required for the core feature to work via API — I'd flag them as a separate, optional increment rather than bundle them in.

**6. Verify**
- `npx tsc --noEmit`.
- Unit-level sanity: empty domain lists → identical output to today; blocklist removes matching hosts; allowlist keeps only listed hosts; malformed `link` → host falls back and is treated as non-matching (kept under blocklist, dropped under a non-empty allowlist — decision to confirm).

## Summary of changed files & risks

| File | Change | Risk |
|---|---|---|
| `src/analysis/criteria.ts` | Add optional `includeDomains`/`excludeDomains`; normalize them; add `filterByDomain` helper | Low — additive, defaults preserve behavior |
| `src/workflows/customerTopNewsWorkflow.ts` | Call `filterByDomain` before prefilter; account dropped items in stats | Low–medium — touches the funnel; must keep empty-set guards and stat honesty |
| `app/api/analyze/route.ts` | Forward two new body fields into `normalizeCriteria` | Low — additive, ignored if absent |
| *(optional)* `lib/storage/types.ts`, `profiles.ts`, UI components | Persist/expose domains | Deferred — not required for core feature |

**Risks / watch-items**
- **Over-filtering:** an aggressive allowlist or blocklist could starve the candidate set. The existing "fallback to `articles.slice()` when candidates empty" guard partially covers this, but a strict allowlist that removes *everything* should produce an honest empty/sparse report, not a crash — confirm the empty-result guard messaging.
- **Stat integrity:** domain-dropped articles must be counted (as dropped/excluded) so `totalFound` vs the funnel still reconciles.
- **Cache:** intentionally **not** changing the cache key (verdicts are per-article and domain-independent) — this keeps cache hits valid; documented above so it's a deliberate choice, not an oversight.
- **Host matching convention:** must match the existing `www.`-stripping used by `sourceDistribution`/feedback so the filter and the stats agree on what a "domain" is.

**Untouched (per safety rules):** auth, billing, secrets, DB schema, deployment config, and the LLM agents/prompts (`criteriaBatchAgent`, `summaryBatchAgent`, `trendAnalysisAgent`) and `llm/client.ts` — none need changes for deterministic domain filtering.

Stopping here as requested — no files modified. Want me to proceed with steps 1–4 (core, API-wired) and leave the UI/persistence for a follow-up?

