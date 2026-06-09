# Approval Model

## Definition

An Approval is a human decision required before risky or irreversible actions.

## Purpose

Approvals protect the system from unsafe autonomous actions.

## Approval Triggers

Approval is required for:

- production deployment
- database schema changes
- deleting code
- modifying secrets
- merging pull requests
- changing billing logic
- changing authentication logic
- infrastructure changes

## Approval Fields

Each approval must define:

- id
- work_item_id
- requested_by_agent
- action
- risk_level
- reason
- required_context
- status
- approved_by
- timestamp

## Approval Status

- pending
- approved
- rejected
- expired
- cancelled

## Rules

Agents cannot approve their own actions.

The Orchestrator pauses execution until approval is resolved.

Human approval overrides agent recommendations.
