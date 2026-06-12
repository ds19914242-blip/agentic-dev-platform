Status: todo

### Task 005 — (Optional) «Проверить все активные» action

**Goal:** Add a one-click run that sequentially (or bounded-parallel) tests all active sources and refreshes the summary.
**Scope:** Button near the status block that iterates active sources, calls the test+persist flow for each with limited concurrency to avoid storage races, shows progress/disabled state, then `load()`s once. Explicitly Out of Scope for the core feature — implement only as a follow-up.
**Suggested files:** `app/sources/page.tsx`, `components/SourceStatusPanel.tsx`.
**Acceptance criteria:** Maps to the optional user story "одним действием запустить проверку всех активных источников". Clicking the action updates every active source's stored status and the block reflects the new aggregate.
**Risk:** medium

## Depends On

_None_
