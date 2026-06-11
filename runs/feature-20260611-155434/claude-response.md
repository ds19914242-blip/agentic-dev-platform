# Claude Response

## Implementation Plan — Task 013: Translate progress views ("Analyzing" headers)

### Findings from inspecting the repository

I inspected the affected files and traced where progress UI text actually lives. Key finding worth flagging up front:

**The one English string in the progress view is NOT in any of the listed affected files.** The only `"Analyzing"` header in the app is here:

- `components/ProgressTimeline.tsx:48` → `<span className="eyebrow">Analyzing</span>`

The rest of that progress view is **already in Russian**: step labels `Парсинг / Префильтр / LLM-анализ / Тренды / Готово` (lines 31–37), `Прошло`, `ETA`, perf stats (`Из кэша`, `Через LLM`, `Батчи`, `Сэкономлено`), and `Ожидание логов…`. The dynamic `currentStep` strings fed from `lib/jobStore.ts` are also already Russian (`В очереди…`, `Парсинг файла…`, `Готово`).

### Why the listed affected files are not the right target

- `app/api/**/route.ts` — these are JSON API endpoints. I grepped them; none contain `"Analyzing"` or any user-facing progress header. `app/api/jobs/[jobId]/route.ts` just returns the job view (its `currentStep` is already Russian). `app/api/analyze/route.ts` only returns `{ jobId }`/error strings. None render a "progress view."
- `src/util/progress.ts` — this is a **CLI** progress reporter writing to `process.stdout` (`Elapsed:`, `ETA:`, `Average:`, `batches`). It is developer/terminal tooling, not the web "progress view ('Analyzing' header)" the task targets. Translating it is out of scope and risks touching non-UI behavior.

The affected-files list appears to be an auto-generated superset (all API routes + the CLI util) and does not match where the visible string actually is. I'm proceeding on the task **title/intent** ("progress views — 'Analyzing' headers"), which points unambiguously to `ProgressTimeline.tsx`.

### Proposed change (smallest safe edit)

Single-line text change in `components/ProgressTimeline.tsx:48`:

```tsx
-          <span className="eyebrow">Analyzing</span>
+          <span className="eyebrow">Анализ</span>
```

Word choice: `Анализ` (noun, matches the eyebrow/label style and the existing `LLM-анализ` step). Reasonable alternatives if a more "in-progress" tone is preferred: `Идёт анализ` or `Анализируем…`. I recommend `Анализ` for consistency and brevity; the others are equally safe and reversible.

### What is intentionally NOT changed

- No API route files (`app/api/**`) — they contain no progress-view header text.
- `src/util/progress.ts` (CLI output) — out of scope; not a web view.
- No auth/billing/secrets/schema/deploy files — none are involved.
- All other ProgressTimeline strings — already Russian.

### Verification steps (after the change is applied in a non-plan run)

1. `npx tsc --noEmit` (or the project's typecheck) — text-only change, should pass trivially.
2. Run the app, trigger an analysis, and confirm the progress card header reads `Анализ` while a job is running.
3. `git diff` should show exactly one changed line.

### Risk

Minimal — a single visible string in one client component, no logic, fully reversible.

---

**One point of uncertainty to confirm:** the task's affected-files list does not include `components/ProgressTimeline.tsx` (the only file containing "Analyzing"), and the listed files contain no such string. I'm confident the intended target is `ProgressTimeline.tsx`, but if the task instead expected something in the API routes or `src/util/progress.ts`, the scope assumption above should be corrected before implementation.

