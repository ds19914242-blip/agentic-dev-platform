# Standard Implementation Response

Typecheck passes. Done.

## Summary

Implemented a persistent inline check badge on each source row in `app/sources/page.tsx`.

**Changes:**
1. **Capture state** — added a `checks` record keyed by source id; `test()` now stores the result (`ok`, `status`, `itemCount`, `error`, `at` timestamp) so it survives after the toast fades. (Task 001's session state wasn't present in this worktree, so the minimal capture was added to make rendering possible.)
2. **Badge render** (near the existing `lastStatus` line) with three variants:
   - **Success** (`check.ok && check.status === "ok"`): green badge `✓ Проверено · {itemCount} {unit} · {time}`, with the correct unit (`элементов` for RSS, `постов` otherwise) reusing the existing unit logic.
   - **Empty** (`status === "empty"`): amber/neutral badge `Пусто · {time}` — clearly not green, no checkmark.
   - **Error** (everything else): rose badge `Ошибка · {time}` — no success badge.
3. **In-progress** — while `testing === s.id`, the row shows a neutral `Проверка…` badge and the success/error indicator is suppressed until the result returns.
4. Added a small `relTime()` helper for short relative time ("только что", "N мин назад", etc.).

The existing `lastStatus`/`lastItemCount` line is left intact, and each row's badge is independent (keyed by `s.id`). Typecheck passes.
