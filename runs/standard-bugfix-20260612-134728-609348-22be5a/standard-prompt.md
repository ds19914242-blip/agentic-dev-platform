# Standard Task Execution

You are fixing a known bug.

Steps:
1. Identify the likely root cause.
2. Make the smallest safe fix.
3. Do not redesign unrelated code.
4. Preserve existing behavior except for the bug.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: bug_fix
Pipeline: standard_bugfix
Risk: low
Status: in_progress

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

