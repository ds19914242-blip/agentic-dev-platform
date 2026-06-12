Type: audit_task
Pipeline: audit
Risk: medium
Status: manual_verification_failed

### Task 006 — End-to-end acceptance verification

**Goal:** Verify the approved feature works end-to-end from the user's perspective.

**Scope:** Product behavior verification. Do not implement new features unless a defect is found and a follow-up bug task is created.

**Acceptance scenarios source:** `acceptance-scenarios.md`

**Required checks:**
# Acceptance Scenarios

## Acceptance Scenarios

1. **Successful RSS check leaves a lasting mark**
   - User opens `/sources`, finds an RSS source, clicks **Проверить**.
   - Button shows "Проверка…"; on success a toast "OK — 12 элементов" appears.
   - The row now shows a persistent green "Проверено · 12 элементов · только что" indicator that remains after the toast fades.

2. **Failed check shows no success indicator**
   - User clicks **Проверить** on a broken source.
   - Toast "Ошибка: недоступен" appears; the row shows a red/error indicator and no green "Проверено" badge.

3. **Empty source is distinct from success**
   - User checks a reachable-but-empty feed.
   - Toast "Доступен, но пуст" appears; the row shows a neutral/info indicator, clearly not a green success.

4. **Per-row isolation**
   - User checks Source A (passes) then Source B (passes).
   - Source A keeps its success indicator while Source B is checking; both end with their own correct indicators; neither overwrites the other.

5. **Telegram unit correctness**
   - User checks a Telegram source returning 30 posts.
   - The indicator reads "…30 постов" (not "элементов").

## Manual Verification Scenarios

- Click **Проверить** on a known-good RSS feed; confirm the green success indicator appears and **remains visible** after the toast disappears (~5s).
- Reload the page; confirm the indicator behaves per the chosen persistence decision (gone if session-only, retained if persisted) — and that this matches what the spec/task agreed.
- Check a deliberately invalid URL source; confirm an error indicator, no green badge.
- Check a reachable feed with zero recent items; confirm the "empty/info" styling, not success.
- Check two different sources in quick succession; confirm indicators are independent and not cross-contaminated.
- Inspect with a screen reader / keyboard; confirm the success state is announced via text/aria, not color alone.
- Repeat for each source type (rss, telegram, reddit, youtube) and confirm the count unit label is correct.

## Acceptance Criteria

- [ ] After a check returns a successful result (`ok === true && status === "ok"`), the corresponding source row shows a persistent success indicator (e.g. a green check/badge labeled "Проверено").
- [ ] The success indicator includes the item/post count returned by the check, using the correct unit per source type ("элементов" for RSS, "постов" for telegram/reddit/youtube).
- [ ] The success indicator shows when the check ran (e.g. a relative or short timestamp) so the user knows the result is recent.
- [ ] The indicator persists on the row after the toast disappears and remains until the source is re-checked or the page is reloaded (persistence scope decided in Scope below).
- [ ] An "empty" result (`status === "empty"`) is visually distinct from a success (neutral/info styling, not green).
- [ ] A failed result (`!ok` or error) is visually distinct from a success (error/red styling) and does not show the success indicator.
- [ ] While a check is in progress for a row, that row shows a "Проверка…" state and the success/error indicator for that row is not shown until the result returns.
- [ ] Checking one source does not alter or clear the indicators of other source rows.
- [ ] The indicator is keyboard- and screen-reader-accessible (status conveyed by text/aria, not color alone).
- [ ] The existing toast behavior is preserved (or intentionally complemented), not removed without replacement.

**Acceptance criteria:**
- All acceptance scenarios pass on the target environment.
- If any scenario fails, mark this task with `agentic.py verify --failed`.
- Failed manual verification automatically creates a bug task.
- If all scenarios pass, mark this task with `agentic.py verify`.

**Risk:** medium

## Depends On

task-001, task-002, task-003, task-004

## Manual Verification Result

Status: manual_verification_failed
Verified At: 2026-06-12T15:03:48
Note: Verification toast appears, but persistent verification indicator is not visible on source cards
Manual Bug Task: backlog/20260612-144038-добавить-видимый-индикатор-успешной-проверки-источника/task-007.md
