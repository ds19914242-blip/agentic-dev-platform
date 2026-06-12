# Standard Implementation Response

Done. Changes to `app/sources/page.tsx`:

1. **Added state map** — `checkResults: Record<string, { status; itemCount?; error?; sourceType; checkedAt }>` keyed by `source.id`.

2. **In `test()`**:
   - At the start of a re-check, only the clicked row's entry is deleted from the map (functional update preserves all other entries).
   - All three outcome branches (`ok`, `empty`, `error`) now record a result object with `status`, `itemCount`/`error` as applicable, `sourceType`, and `checkedAt: Date.now()`.
   - The result is written via `setCheckResults((prev) => ({ ...prev, [s.id]: result }))`, so per-row isolation holds — other entries are untouched.

Existing toast calls are unchanged, and nothing new is rendered yet (as specified).
