# Rollback Model

## Definition

Rollback is the process of reversing or recovering from unsafe, failed or incorrect actions.

## Purpose

The system must be able to recover when agents, tools or deployments fail.

## Rollback Triggers

Rollback may be required when:

- tests fail
- deployment fails
- production is degraded
- user impact is detected
- security risk is discovered
- incorrect code is merged
- database migration fails

## Rollback Strategies

- revert code changes
- revert pull request
- restore previous deployment
- restore database backup
- disable feature flag
- pause execution
- request human intervention

## Rules

High-risk actions must define a rollback strategy before execution.

Production changes require rollback planning.

Rollback actions must be recorded.

If rollback is not possible, human approval is required before execution.
