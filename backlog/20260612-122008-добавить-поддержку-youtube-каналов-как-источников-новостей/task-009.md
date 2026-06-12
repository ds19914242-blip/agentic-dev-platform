PR: https://github.com/ds19914242-blip/rss-agent-lab/pull/55
Run: standard-bugfix-20260612-134728-609348-22be5a
Type: bug_fix
Pipeline: standard_bugfix
Risk: low
Status: pr_created

### Task 009 — Fix YouTube still missing on production Sources UI

**Goal:** Make YouTube appear in the production Sources UI source type selector.

**Problem:** PR #54 was merged, build/deploy completed, but production `/sources` still shows RSS, Telegram and Reddit only. YouTube is still missing.

**Scope:** Sources UI only.

**Acceptance criteria:**
- YouTube appears visibly in the source type selector on `/sources`.
- The visible label is `YouTube-канал`.
- Selecting YouTube shows a YouTube-specific input placeholder such as `@OpenAI` or YouTube channel URL.
- Existing RSS, Telegram and Reddit source options remain visible and working.
- Validation passes.

**Risk:** low

## Depends On

task-008
