Type: implementation_task
Pipeline: standard
Risk: low
Status: pr_created

### Task 007 — Recognize Reddit sources in article display and favorites

**Goal:** Ensure saved/displayed articles correctly attribute Reddit as their source type.
**Scope:** Update the article source-type detection (currently hostname-based: `t.me → telegram`, else `rss`) so Reddit links (`reddit.com` / `redd.it`) are tagged `"reddit"`, and ensure favorites/reading-list store the `"reddit"` `sourceType`. Add any minimal styling/label for a Reddit source where Telegram/RSS are already distinguished.
**Suggested files:** `components/NewsCard.tsx`, `lib/saveFavorite.ts` (and `lib/storage/types.ts` `FavoriteArticle.sourceType` comment if it enumerates kinds)
**Acceptance criteria:**
- Articles with Reddit links are detected and labeled as `"reddit"` rather than falling back to `"rss"`.
- Saving a Reddit article to favorites persists `sourceType: "reddit"`.
- Telegram/RSS detection and display are unchanged.
- `tsc` passes.
**Risk:** low

#### Depends On
task-001

## Depends On

_None_
