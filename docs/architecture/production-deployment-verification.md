# Production Deployment Verification

Production Deployment Verification confirms that a merged PR is actually visible and working on the production URL.

## Command

python3 agentic.py release-check backlog/<epic>/task-XXX.md --product rss-agent-lab_2

## Flow

1. Load product config.
2. Resolve production URL.
3. Mark task as production_verification_running.
4. Check production HTTP availability.
5. Run acceptance against production.
6. Write:
   - release-verification.md
   - release-verification.json
7. Mark:
   - release_confirmed
   - or release_failed

## Statuses

production_verification_running
release_confirmed
release_failed
