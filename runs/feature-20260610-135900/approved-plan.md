# Approved Plan

# Claude Response

## Investigation summary

I inspected the affected files plus the surrounding wiring. The key finding: **the deterministic backend filter is already fully implemented and committed** (HEAD commit `6a44183`, the same title as this request). What's actually missing is the **user-facing path** — there's no way to enter domains, so the feature is unreachable in the product.

### What already exists (do not touch)
- `src/analysis/criteria.ts` — `includeDomains`/`excludeDomains` on `AnalysisCriteria`, plus `normalizeDomain`, `normalizeDomains`, `domainOf`, `hostMatchesDomain`, `passesDomainFilter` (subdomain-aware, allow+block). `normalizeCriteria` already parses them.
- `src/prefilter/prefilterArticles.ts` — applies `passesDomainFilter` before keyword scoring, so blocked domains never reach the LLM and show as `dropped`.
- `src/workflows/customerTopNewsWorkflow.ts` — threads `criteria.includeDomains/excludeDomains` into the prefilter.
- `app/api/analyze/route.ts` — reads `body.includeDomains/excludeDomains` into `normalizeCriteria`.

### The gap
- `app/page.tsx` — has no domain state and does **not** send `includeDomains`/`excludeDomains` in the `/api/analyze` body (lines 131–140). So the API always receives empty domain lists.
- `components/TopicSelector.tsx` — no UI to enter domains.
- (Optional) `lib/storage/types.ts` `Profile` + `src/analysis/profiles.ts` `BUILTIN_PROFILES` + `applyProfile` in `page.tsx` — profiles can't persist domain filters.

### Note on the task's "Affected Files" list
The list (agents `criteriaBatchAgent`/`summaryBatchAgent`/`trendAnalysisAgent`, `feedbackRanking.ts`, `performance.ts`, `llm/client.ts`) is a **superset that does not need editing** for the smallest safe implementation:
- The three agents run *after* the deterministic prefilter; domain filtering happens before any LLM call, so prompts/schemas are unaffected.
- `performance.ts` and `llm/client.ts` are unrelated to source filtering.
- `feedbackRanking.ts` has its own `hostOf` helper duplicating `domainOf` — an optional dedup refactor only, not required.

I'd stop and flag rather than make changes there.

---

## Proposed implementation plan (smallest safe path)

### Phase 1 — Wire the UI to the existing backend (required)

**1. `components/TopicSelector.tsx`**
- Add two optional props: `includeDomains: string[]`, `excludeDomains: string[]`, plus `onIncludeDomainsChange` / `onExcludeDomainsChange`.
- Reuse the existing `KeywordEditor` component (it already handles arbitrary string chips with add/remove) for two new editors — labels e.g. "Только эти источники (домены)" and "Исключить источники (домены)", placeholder "напр. example.com или https://example.com/…".
- Render them in a new `border-t` section, mirroring the existing include/exclude keyword grid. Backend `normalizeDomain` already accepts full URLs or bare hosts and strips `www.`, so no client-side validation is needed.

**2. `app/page.tsx`**
- Add state: `const [includeDomains, setIncludeDomains] = useState<string[]>([])` and `excludeDomains` (default `[]` to preserve current "all domains" behavior).
- In `onRunAnalysis` (line 131), add `includeDomains` and `excludeDomains` to the JSON body.
- Pass the new props/handlers into `<TopicSelector>` (line 251).

That's the complete required change — three small, reversible edits, no backend changes.

### Phase 2 — Profile persistence (optional; only if domains should survive in saved profiles)

**3. `lib/storage/types.ts`** — add optional `includeDomains?: string[]` / `excludeDomains?: string[]` to the `Profile` interface (optional → back-compatible with stored profiles).

**4. `src/analysis/profiles.ts`** — optionally add domain examples to relevant `BUILTIN_PROFILES` (or leave them absent → behaves as "all domains").

**5. `app/page.tsx` `applyProfile`** (line 84) — set `setIncludeDomains(p.includeDomains ?? [])` / `setExcludeDomains(p.excludeDomains ?? [])`.

**6. `app/profiles/page.tsx`** — add domain editors to the custom-profile form (this is the larger piece; defer unless profile persistence is explicitly required).

I'd recommend **Phase 1 only** as the minimal change that makes the already-built filter usable, and treat Phase 2 as a follow-up.

### Verification
- `npm run typecheck` (script exists in package.json).
- Manual: upload/collect → enter an `excludeDomains` host → confirm articles from that host disappear from the report; enter an `includeDomains` host → confirm only that source survives. Subdomains (e.g. `news.example.com` under `example.com`) should match.

### Open question
Should domain filters be **persisted in profiles** (Phase 2 + the profiles-page editor), or is the **per-run UI input** (Phase 1) sufficient for now? This is the one branch point that changes scope — I'd default to Phase 1 unless you want profile persistence.

No files were modified.


