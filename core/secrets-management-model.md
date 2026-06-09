# Secrets Management Model

## Definition

Secrets are sensitive values required by products, tools or environments.

Examples:

- API keys
- database credentials
- tokens
- OAuth secrets
- deployment keys
- webhook secrets

## Principle

Agents must never receive raw secrets unless explicitly authorized.

Secrets are managed through controlled access.

## Purpose

The platform must protect sensitive credentials while still allowing agents to work with environments and tools.

## Access Rules

Secrets access is controlled by:

- Orchestrator
- Governance
- Approval
- Environment policy
- Tool permissions

## Secret Actions

- create secret
- reference secret
- rotate secret
- revoke secret
- validate secret exists

## Restricted Actions

Require approval:

- reading raw secret values
- creating production secrets
- rotating production secrets
- deleting secrets
- sharing secrets with external tools

## Rules

Secrets must not be stored in agent memory.

Secrets must not be written into code.

Secrets must not appear in logs.

Secret access must be audited.

Production secret actions require approval.
