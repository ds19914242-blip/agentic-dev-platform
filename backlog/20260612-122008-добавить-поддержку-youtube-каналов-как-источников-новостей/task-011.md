PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/57
Run: standard-bugfix-20260612-142100-690798-db843b
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Status: pr_created

### Bug Fix — Collection pipeline returns no articles for Reddit and YouTube

**Problem:**
UI shows Reddit and YouTube source types.
Sources can be created and saved.
Production deployment succeeds.

However, running collection returns:

"No articles collected (check that sources are active and reachable)."

Previous fixes only addressed UI visibility.

**Goal:**
Find and fix the actual collection failure.

**Required investigation:**
- Verify source persistence after save.
- Verify sourceType is stored correctly.
- Verify reddit/youtube config is persisted.
- Verify collect route loads saved sources.
- Verify lib/rss/collect.ts dispatches reddit/youtube branches.
- Verify fetchRedditSubreddit().
- Verify fetchYouTubeChannel().
- Verify normalized articles reach aggregation.
- Verify non-empty results are returned by collect API.

**Acceptance criteria:**
- Reddit source returns articles.
- YouTube source returns articles.
- Run Analysis succeeds on production.
- Mixed RSS + Reddit + YouTube collection works.
- Validation passes.

**Risk:** medium

## Depends On

task-010
