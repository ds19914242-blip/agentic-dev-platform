# Claude Response

I'll respect the explicit "stop after the plan" instruction in the task body and hold here. The plan above is complete and ready to execute.

**Recommended approach when you confirm:** Implement (no UI) with **include + exclude** semantics — it mirrors the existing `includeKeywords`/`excludeKeywords` pattern exactly, stays in the deterministic prefilter layer (no LLM cost, no cache-key or schema changes), and is fully reversible.

Just reply with how you'd like to proceed (e.g. "implement, exclude-only" or "implement + UI") and I'll make the edits and run `npx tsc --noEmit`.

