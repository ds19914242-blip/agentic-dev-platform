# Claude Response

## Implementation Plan: Article source filtering by domain

### Key finding first (important)

The **deterministic core of this feature already exists** — it was added in today's commit `6a44183`. Working end‑to‑end at the data/pipeline layer:

- `src/analysis/criteria.ts` — `includeDomains`/`excludeDomains` fields, `normalizeDomain`, `normalizeDomains`, `domainOf`, `hostMatchesDomain`, `passesDomainFilter` (subdomain‑aware), and normalization in `normalizeCriteria`.
- `src/prefilter/prefilterArticles.ts` — applies the domain filter *before* keyword scoring, so blocked domains never reach the LLM or backfill.
- `src/workflows/customerTopNewsWorkflow.ts` — passes domains into the prefilter and re‑applies the filter in the empty‑candidate fallback.
- `app/api/analyze/route.ts` — reads `includeDomains`/`excludeDomains` from the request body into `normalizeCriteria`.

A repo‑wide search confirms `includeDomains`/`excludeDomains` appear in **only those 4 files**. `startAnalysis` (`lib/jobStore.ts`) takes already‑normalized criteria, so domains flow through automatically — no change needed there.

### The genuine gap

The filter is **honored by the backend but unreachable from the UI**, and **not persistable**:

1. **No UI input** — `app/page.tsx` sends only `selectedTopics`/`includeKeywords`/`excludeKeywords` to `/api/analyze`; there's no field for domains, and `TopicSelector.tsx` has no domain controls. So no user can actually trigger a domain filter today.
2. **Profiles can't store domains** — the `Profile` interface (`lib/storage/types.ts`) and `BUILTIN_PROFILES` (`src/analysis/profiles.ts`) have no domain fields, so a saved profile drops domain preferences. `profiles.ts` is in the affected‑files list — this is the one listed file that genuinely needs work.

### Uncertainty to flag re: the affected-files list

The task's affected‑files list does **not** match the smallest safe implementation. Specifically, these listed files do **not** need changes, and I'd avoid touching them:

- `src/agents/criteriaBatchAgent.ts`, `summaryBatchAgent.ts`, `trendAnalysisAgent.ts` — domain filtering is deterministic and runs *before* any LLM call; the agents only ever see articles that already passed the filter. No change.
- `src/analysis/performance.ts` — speed/depth presets, unrelated to source filtering.
- `src/llm/client.ts` — Anthropic client/model config, unrelated.
- `src/analysis/feedbackRanking.ts` — host‑based *affinity* re‑ranking, a separate concern from a hard allow/block filter.

I read all of these to confirm. If the intent was something broader (e.g. per‑agent domain awareness, or domain‑based feedback affinity), I'd want that clarified before touching them — otherwise I'd be adding unused plumbing against the "smallest safe change" rule.

The components below (the actual UI + persistence) are **not** in the affected‑files list. So either (a) the feature is considered "done" at the backend layer already committed, or (b) the real remaining work lives in files the list didn't name. My plan assumes the goal is a **usable** feature and targets the real gap.

---

### Proposed plan (smallest safe completion)

**Step 1 — Profile persistence (`profiles.ts` + `Profile` type)**
- In `lib/storage/types.ts`, add optional `includeDomains?: string[]` and `excludeDomains?: string[]` to `Profile` (optional = back‑compat with stored custom profiles).
- In `src/analysis/profiles.ts`, leave existing built‑ins as‑is (they simply omit the fields = "all domains"). Optionally seed one or two built‑ins with example `includeDomains` only if desired — not required.
- Verify the profiles API routes (`app/api/profiles/*`) pass the new optional fields through (they likely spread the object; confirm during implementation).

**Step 2 — Configure UI (`app/page.tsx`, `TopicSelector.tsx`)** *(not in the affected list — flagged)*
- Add two comma/line‑separated text inputs ("Только эти источники" / "Исключить источники") with `includeDomains`/`excludeDomains` state, mirroring the existing include/exclude keyword inputs.
- Send both in the `/api/analyze` POST body (the route already reads them).
- Apply a profile's domains when a profile is selected (alongside the existing `setInclude`/`setExclude`).
- No backend change required — `normalizeCriteria` already sanitizes raw user input (URLs → bare hosts, dedupe, blank‑strip).

**Step 3 — (Optional) History record (`Run` type)**
- Add optional `includeDomains?`/`excludeDomains?` to `Run` in `lib/storage/types.ts` and populate in `startAnalysis` if we want runs to show the domain filter used. Purely additive; skip if out of scope.

**Step 4 — Verification**
- `npx tsc --noEmit` (project uses `tsconfig.tsbuildinfo`).
- Manual: select a profile / type a domain, run an analysis on a sample `.txt`, confirm only matching hosts appear in `sourceDistribution`. Existing `passesDomainFilter` subdomain semantics already cover `news.x.com ⊂ x.com`.

### Recommendation

Because the backend is already complete and committed, the highest‑value, smallest change is **Step 1 (profiles persistence) + Step 2 (UI wiring)**. I'd skip the agents/`performance.ts`/`llm/client.ts`/`feedbackRanking.ts` edits the affected‑files list implies, since they'd be dead code.

Before I implement, one decision worth confirming: should I proceed with the UI + profiles completion as above (recommended), or is the expectation strictly to modify the listed files (agents/performance/llm/client)? The latter doesn't have a clear, safe purpose for this feature, so I'd want to align on intent first.

Per `plan_only` mode, I've made no changes. Stopping here.

