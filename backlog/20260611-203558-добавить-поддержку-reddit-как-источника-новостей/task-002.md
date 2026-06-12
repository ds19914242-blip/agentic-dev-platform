PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/40
Run: standard-20260611-204221-688189-991949
Type: implementation_task
Pipeline: standard
Risk: medium
Status: pr_created

### Task 002 — Build the Reddit fetcher module

**Goal:** Implement a self-contained Reddit subreddit fetcher mirroring `fetchTelegramChannel.ts`, producing normalized articles.
**Scope:** Create a fetcher that takes a subreddit + `maxPosts`/`timeWindowDays`, calls Reddit's public JSON endpoint with a proper `User-Agent`, parses posts, applies the time-window filter, caps post count, and returns the same result shape used by the collector (status, itemCount, error, and `NormalizedArticle[]`). Include a `normalizeReddit(input)` helper that accepts `r/<sub>`, `<sub>`, and full URLs and returns `{ subredditName, webUrl }`. Define default/cap constants (e.g. default max posts, hard cap, default window days).
**Suggested files:** `lib/reddit/fetchRedditSubreddit.ts` (new), referencing `lib/rss/fetchFeed.ts` `NormalizedArticle` for the output shape and `lib/telegram/fetchTelegramChannel.ts` as the structural template.
**Acceptance criteria:**
- `normalizeReddit` correctly parses the documented input forms and rejects invalid input (returns `null` or throws consistently with Telegram's pattern).
- Fetcher returns normalized articles with `title`, `link`, `summary`, `publishedAt`, `sourceName`, and a `sourceType: "reddit"` marker where the Telegram equivalent sets one.
- Network/parse failures return a structured error result instead of throwing uncaught.
- Time-window filtering and max-post cap are applied.
- `tsc` passes; module is importable and has no side effects on import.
**Risk:** medium

#### Depends On
task-001

---

## Depends On

_None_
