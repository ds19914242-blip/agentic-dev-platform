# Workflow Lifecycle Model

## Definition

The Workflow Lifecycle defines how Workflow Templates are created, updated, approved and retired.

## Purpose

Workflow Templates are managed assets of the platform.

## Lifecycle Stages

- proposed
- experimental
- active
- deprecated
- retired

## Template Creation Flow

Need Identified
→ Workflow Proposal
→ Workflow Design
→ Validation
→ Approval
→ Active Template

## Template Update Flow

Template Change
→ Validation
→ Evaluation
→ Approval
→ New Version

## Template Retirement Flow

Deprecation Decision
→ Migration Plan
→ Retirement

## Versioning

Workflow Templates must be versioned.

Execution Graphs must record which template version was used.

## Rules

Active templates may be used by new executions.

Deprecated templates may finish existing executions.

Retired templates may not be used for new executions.

Template changes must be auditable.
