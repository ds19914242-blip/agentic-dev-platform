# Standard Task Execution

You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.


Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

Type: implementation_task
Pipeline: standard
Risk: low
Status: in_progress

### Task 008 — Show YouTube in Sources UI

**Goal:** Make YouTube visible and selectable in the Sources UI.

**Problem:** Production Sources UI shows RSS, Telegram and Reddit, but YouTube is missing.

**Scope:** Sources UI only.

**Acceptance criteria:**
- YouTube appears as a source type option next to RSS, Telegram and Reddit.
- Selecting YouTube shows channel-specific input placeholder, e.g. `@OpenAI` or YouTube channel URL.
- Existing RSS, Telegram and Reddit options still work.
- Validation passes.

**Risk:** low

## Depends On

task-006

