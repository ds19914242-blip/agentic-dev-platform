# Workflow Template Model

## Definition

A Workflow Template is a reusable blueprint for creating Execution Graphs.

Workflow Templates are not executed directly.

They are selected and adapted by the Orchestrator.

## Purpose

Workflow Templates prevent the system from inventing the development process from zero every time.

They provide structure, safety and consistency.

## Examples

- New Product Template
- Feature Request Template
- Bug Fix Template
- Refactor Template
- Release Template
- Incident Template

## Relationship to Execution Graph

Workflow Template
→ adapted by Orchestrator
→ Execution Graph

Templates are static blueprints.

Execution Graphs are dynamic runtime objects.

## Template Fields

Each Workflow Template must define:

- id
- name
- work_item_types
- default_stages
- required_agents
- optional_agents
- required_tools
- approval_gates
- risk_rules
- required_artifacts
- completion_criteria

## Dynamic Adaptation

The Orchestrator may adapt a template by:

- adding nodes
- removing nodes
- splitting nodes
- merging nodes
- changing dependencies
- adding approval gates
- assigning different agents

## Rules

1. Every Execution Graph should be based on a Workflow Template.

2. The Orchestrator may adapt templates, but must record changes.

3. High-risk templates require stronger approval gates.

4. Templates should be versioned.

5. Template changes must be reviewed.
