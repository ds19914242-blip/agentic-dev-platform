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

## Agent Output Contract

Every agent must return structured output.

Minimum output:

- summary
- findings
- decisions
- risks
- required_actions
- next_steps
- confidence

## Agent Status

Possible agent execution statuses:

- pending
- running
- completed
- failed
- blocked
- requires_approval

## Agent Permissions

Agents can only use tools and access resources explicitly granted by the Orchestrator.

Default permission level:

- read context
- analyze information
- propose actions

Agents cannot by default:

- modify code
- access secrets
- deploy
- delete files
- merge pull requests
