# Task Breakdown Model

## Definition

Task Breakdown is an Artifact that decomposes a Work Item into executable tasks.

## Purpose

Task Breakdown connects planning with implementation.

It turns product and architecture decisions into concrete execution units.

## Task Fields

Each task must define:

- id
- title
- description
- type
- dependencies
- assigned_agent_type
- required_tools
- required_artifacts
- risk_level
- acceptance_criteria

## Task Types

- frontend
- backend
- database
- infrastructure
- testing
- documentation
- security
- release

## Relationship to Execution Graph

Task Breakdown
→ validated by Orchestrator
→ converted into Execution Graph nodes

## Rules

Task Breakdown must be created before implementation.

Task Breakdown must be stored as an Artifact.

Tasks with dependencies must be ordered in the Execution Graph.

High-risk tasks require approval gates.
