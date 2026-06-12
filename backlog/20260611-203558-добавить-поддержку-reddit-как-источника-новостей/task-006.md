Type: feature_task
Pipeline: full
Risk: medium
Status: done_no_pr

### Task 006 — Add Reddit to the Sources UI (selector, form, badge)

**Goal:** Surface Reddit in the sources management page so users can add, edit, and identify Reddit sources.
**Scope:** Add a "Reddit" option to the source-type selector; render a Reddit-specific form branch (subreddit input + `maxPosts` + `timeWindowDays`) reusing the Telegram form pattern; wire the test button to the Reddit test path; display a distinct "Reddit" badge and a Reddit-appropriate detail line (e.g. `r/<sub> · N постов / Xд`) in the source list.
**Suggested files:** `app/sources/page.tsx` (and `app/rss/page.tsx` if it duplicates the source form/badge rendering)
**Acceptance criteria:**
- The UI offers RSS / Telegram / Reddit as selectable source types.
- Selecting Reddit shows the subreddit + posts/window controls and submits `sourceType: "reddit"`.
- The source list renders a "Reddit" badge and correct detail line for Reddit sources.
- Existing RSS/Telegram UI is unchanged.
- `tsc` passes; page compiles and renders.
**Risk:** medium

#### Depends On
task-004

---

## Depends On

_None_
