# Agent Lifecycle Model

## Definition

The Agent Lifecycle defines how agents are created, updated, validated, deployed and retired.

## Purpose

Agents are managed assets of the platform.

The platform must control agent evolution.

## Lifecycle Stages

- proposed
- experimental
- active
- deprecated
- retired

## Agent Creation Flow

Need Identified
→ Agent Proposal
→ Agent Design
→ Validation
→ Registration
→ Active Agent

## Agent Update Flow

Agent Change
→ Validation
→ Evaluation
→ Approval
→ Deployment

## Agent Retirement Flow

Deprecation Decision
→ Migration Plan
→ Retirement

## Validation Requirements

Before activation an agent must be evaluated for:

- capability
- safety
- reliability
- tool usage
- permissions
- cost profile

## Rules

Agents must be versioned.

Agent changes must be auditable.

Deprecated agents may not be assigned to new executions.

Retired agents remain in execution history.
