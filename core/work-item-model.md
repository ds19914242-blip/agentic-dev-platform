# Work Item Model

## Definition

A Work Item is a request for work handled by the system.

It may represent a feature, bug fix, refactor, research task, release, incident or new product.

## Work Item Types

- new_product
- feature
- bug_fix
- refactor
- research
- release
- incident
- maintenance

## Work Item Fields

Each Work Item must define:

- id
- title
- type
- description
- requester
- target_repository
- target_environment
- priority
- constraints
- success_criteria
- risk_level
- status
- created_at
- updated_at

## Work Item Status

- draft
- accepted
- analyzing
- planned
- executing
- waiting_for_approval
- validating
- completed
- failed
- cancelled
- blocked

## Rules

Every Execution Graph must belong to a Work Item.

Every code change must be connected to a Work Item.

A Work Item is complete only when success criteria are met.
