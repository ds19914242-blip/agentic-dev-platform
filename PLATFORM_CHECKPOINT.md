# Platform Checkpoint — v0.3-platform-verification

## Current capabilities

- Feature spec before decomposition.
- Human approval via `agentic.py approve-spec`.
- Acceptance scenarios extraction.
- Auto-generated final E2E/manual verification task.
- Manual verification statuses:
  - manual_verification_required
  - manual_verification_passed
  - manual_verification_failed
- `agentic.py verify` marks manual results.
- Failed manual verification auto-creates bug task.
- Validation still uses build/typecheck, not browser E2E.

## Known gaps

- No automatic Playwright/browser execution yet.
- Manual verification is human-driven.
- DAG dependency parsing can still break on malformed task text.
- PR conflict recovery is manual.
- `done_no_pr` still exists in legacy paths.

## Return point

Use git tag:

`v0.3-platform-verification`
