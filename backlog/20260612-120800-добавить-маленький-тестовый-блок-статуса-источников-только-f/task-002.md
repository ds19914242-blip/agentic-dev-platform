Status: todo

### Task 002 — Serialize source-storage writes to prevent lost updates

**Goal:** Harden `LocalRssSourceStorage` so concurrent `update` calls (e.g. several sources tested in quick succession, each a read-modify-write over one JSON file) cannot clobber each other.
**Scope:** Add an in-process write serialization (e.g. a promise chain / mutex) around the read-modify-write in `LocalRssSourceStorage.update` (and other mutating methods that read-then-write the same file) so operations queue rather than interleave. No public API or return-shape change; same method signatures.
**Suggested files:** `lib/storage/rss.ts`.
**Acceptance criteria:** Maps to Risk "Гонки при параллельных проверках … могут терять записи". Firing multiple overlapping `update` calls on different source ids results in all updates persisted (none lost). Existing list/get/create/delete behavior unchanged.
**Risk:** medium

## Depends On

_None_
