Status: todo

### Task 006 — QA pass and aggregation unit test

**Goal:** Validate the manual scenarios and lock the aggregation logic with a lightweight test.
**Scope:** Execute the spec's Manual Verification Scenarios (mixed types, ok/error/empty persistence + reload, toggle active, no-sources, slow-network skeleton, last-checked refresh). Add a small component/unit test for the counter aggregation in `SourceStatusPanel` (status bucketing incl. `empty`≠`error` and not-checked) if a test setup exists.
**Suggested files:** test file alongside `components/SourceStatusPanel.tsx` (per repo test conventions), `app/sources/page.tsx` (read-only reference).
**Acceptance criteria:** Maps to "Manual Verification Scenarios" and the "лёгкий компонентный тест агрегации" note. All listed scenarios pass; aggregation test covers ok/empty/error/not-checked and active vs total.
**Risk:** low

## Depends On

- Task 001 → task-002
- Task 002 → _None_
- Task 003 → _None_
- Task 004 → task-001, task-003
- Task 005 → task-004
- Task 006 → task-003, task-004

_Note: per-task `## Depends On` sections, as required:_

**Task 001 Depends On:** task-002
**Task 002 Depends On:** _None_
**Task 003 Depends On:** _None_
**Task 004 Depends On:** task-001, task-003
**Task 005 Depends On:** task-004
**Task 006 Depends On:** task-003, task-004
