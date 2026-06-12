Status: todo

### Task 001 — Persist test results into the source record

**Goal:** Make pressing «Проверить» durable — `POST /api/rss/test` records `lastStatus`, `lastItemCount`, `lastError`, `lastFetchedAt` onto the tested source so the status survives a page reload.
**Scope:** Extend `POST /api/rss/test` to accept an optional source `id` in the request body (chosen fork from Decomposition Note 1 — keep one round-trip rather than a separate client PATCH). After computing the fetch result for all three branches (rss/telegram/reddit), when `id` is present and resolves to an existing source, call `rssSourceStorage.update(id, {...})` with the four status fields (`lastStatus` from `res.status`, `lastItemCount` from `res.itemCount`, `lastError` from `res.error` or undefined on success, `lastFetchedAt` = now ISO). The test response shape stays the same; persistence is best-effort and must never throw or change the HTTP status. Do not expand what error text is stored beyond what the list already shows. No schema change.
**Suggested files:** `app/api/rss/test/route.ts`, `lib/storage/rss.ts` (read-only reference), `lib/storage/types.ts` (read-only reference).
**Acceptance criteria:** Maps to AC "результат … сохраняется в хранилище и виден после перезагрузки" and "Никакие чувствительные данные … не раскрываются". After a test of a working RSS source, the stored source has `lastStatus="ok"` and a fresh `lastFetchedAt`; a broken URL stores `lastStatus="error"` with `lastError`; an empty-but-reachable source stores `lastStatus="empty"` (not error). Calling `/api/rss/test` without an `id` behaves exactly as today.
**Risk:** medium

## Depends On

_None_
