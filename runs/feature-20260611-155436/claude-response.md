# Claude Response

I have everything I need. The investigation is conclusive.

## Findings

**The actual scope is tiny.** `components/StatsPanel.tsx` is already almost fully translated to Russian — every data row label is in Russian. Only **two section headings remain in English**:

- Line 22: `<h2 className="label mb-3">Processing</h2>`
- Line 35: `<h2 className="label mb-3">Performance</h2>`

**The 12 "Affected Files" (API routes) are a false lead.** I inspected them:
- `app/api/overview/route.ts` returns only JSON data (counts, reports) — no UI strings, and nothing StatsPanel-related.
- The only `Processing`/`Performance` matches across all API routes are TypeScript identifiers (`PerformanceMode`, `isPerformanceMode`) — type names, not user-facing text.
- StatsPanel receives `ProcessingStats`/`TechnicalStats` as typed props; all displayed labels are hardcoded in the component itself, not sourced from the API.

So no API route needs changing. Editing them would be out of scope and risky (the rules forbid touching auth routes like `login`/`logout` unless required — they aren't).

---

## Implementation Plan

**Goal:** Translate the two remaining English headings in StatsPanel to Russian.

**Single file to modify:** `components/StatsPanel.tsx`

**Change 1 — line 22:**
```
-        <h2 className="label mb-3">Processing</h2>
+        <h2 className="label mb-3">Обработка</h2>
```

**Change 2 — line 35:**
```
-        <h2 className="label mb-3">Performance</h2>
+        <h2 className="label mb-3">Производительность</h2>
```

**Term rationale:**
- `Processing` → **Обработка** — matches the section's row labels (filtering/LLM processing of news items).
- `Performance` → **Производительность** — matches the section's content (execution time, cache savings). These terms aren't used elsewhere in `components/`, so there's no existing convention to conflict with; both are the standard Russian renderings.

**Scope guarantees:**
- No structural/JSX/className changes — text-node only.
- No props, types, or data flow touched.
- No API routes, auth, billing, secrets, schema, or config touched.
- Fully reversible (two one-line string swaps).

**Verification after applying:**
1. `npx tsc --noEmit` (or the project's typecheck) — should pass; text-only change carries no type risk.
2. Visually load the Dashboard's report view and confirm both headings render in Russian.

---

Per `plan_only` mode, I've stopped here and made **no modifications**. Ready to apply the two edits on your go-ahead.

