# Environment Model

## Definition

An Environment is a runtime context where software runs.

Examples:

- local
- development
- staging
- production

## Environment Fields

Each environment must define:

- id
- name
- type
- url
- status
- repository
- branch
- deployment_platform
- secrets_policy
- approval_policy

## Environment Types

### Local

Used for development and testing.

### Staging

Used for validation before production.

### Production

Used by real users.

## Access Rules

Agents may freely analyze local and staging environments if permitted.

Production access requires explicit approval.

## Restricted Actions

Require approval:

- deploy to production
- modify secrets
- change environment variables
- run database migrations
- restart production services
- delete production resources

## Rules

The Orchestrator controls all environment access.

Agents cannot modify environments directly.
