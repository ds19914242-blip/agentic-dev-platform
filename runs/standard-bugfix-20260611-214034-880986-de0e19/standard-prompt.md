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
Risk: medium
Status: in_progress
Source: validation_failed
Run: standard-20260611-213452-735629-6f5335

### Bug Fix — Recover failed run standard-20260611-213452-735629-6f5335

**Problem:** A previous Agentic Dev Platform run failed or did not complete successfully.

**Source task:** task-012.md

**Evidence:**
- runs/standard-20260611-213452-735629-6f5335/validation.md
- runs/standard-20260611-213452-735629-6f5335/run.json

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- Validation passes.
- The original task can be completed or safely marked resolved.
- No unrelated files are changed.

**Risk:** medium

## Depends On

_None_

