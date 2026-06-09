# Identity and Permission Model

## Definition

Identities represent humans, agents and system actors interacting with the platform.

Permissions define allowed actions.

## Identity Types

### Owner

Full system authority.

### Admin

Platform administration authority.

### Product Owner

Authority over assigned products.

### Developer

Authority to create and modify work.

### Reviewer

Authority to review and approve work.

### Observer

Read-only access.

### Agent

System-controlled execution identity.

## Permission Categories

- read
- create
- modify
- approve
- deploy
- administer
- manage_secrets

## Permission Scope

Permissions may apply to:

- Product
- Repository
- Environment
- Work Item
- Artifact
- Approval
- Tool

## Approval Authority

Only authorized identities may approve:

- deployments
- secret changes
- infrastructure changes
- production changes

## Agent Permissions

Agents receive temporary permissions from the Orchestrator.

Agents do not own permanent permissions.

## Rules

All actions must be attributable to an identity.

Permission grants must be auditable.

Human permissions override agent permissions.
