# Agent Model

## Definition

An Agent is a specialized execution unit controlled by the Orchestrator.

Agents do not own the system state.

Agents receive context, perform work and return structured results.

## Agent Fields

Each agent must define:

- id
- name
- type
- mission
- responsibilities
- inputs
- outputs
- allowed tools
- permissions
- memory access
- approval requirements
- restrictions

## Control Rule

Agents cannot act independently.

Every agent action must be initiated, approved or recorded by the Orchestrator.
