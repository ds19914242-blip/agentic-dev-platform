# Execution Graph Model

## Definition

An Execution Graph is a directed graph of work created and managed by the Orchestrator.

It defines:

- what needs to be done
- which agents are required
- execution dependencies
- parallel execution opportunities
- approval gates
- completion requirements

## Principle

The system executes graphs, not workflows.

Workflows are templates.

Execution Graphs are runtime objects generated for specific Work Items.

## Ownership

Execution Graphs are created, modified and managed by the Orchestrator.

Agents do not own or modify execution graphs directly.

---

## Graph Components

### Node

A unit of work.

Examples:

- Product Analysis
- Architecture Analysis
- Security Review
- Backend Implementation
- Frontend Implementation
- QA Validation
- Release Preparation

### Edge

A dependency between nodes.

Example:

Architecture Analysis
→ Backend Implementation

### Parallel Nodes

Independent nodes may execute simultaneously.

Example:

- Product Analysis
- Architecture Analysis
- Security Analysis

---

## Node Types

- analysis
- planning
- implementation
- validation
- approval
- release
- memory_update

---

## Node Status

- pending
- running
- completed
- failed
- blocked
- skipped
- requires_approval

---

## Node Fields

Each node must define:

- id
- name
- type
- assigned_agent
- inputs
- outputs
- dependencies
- required_tools
- required_permissions
- approval_required
- completion_criteria

---

## Execution Rules

A node may start only when all required dependencies are completed.

Independent nodes may run in parallel.

The Orchestrator determines execution order.

The Orchestrator may dynamically assign or reassign agents.

---

## Approval Gates

Approval nodes pause graph execution until approval is received.

Examples:

- production deployment
- database schema modification
- secrets access
- pull request merge

---

## Failure Handling

If a node fails, the Orchestrator may:

- retry the node
- assign another agent
- request human input
- modify the execution graph
- stop execution

---

## Dynamic Graph Updates

Execution Graphs are not fixed.

The Orchestrator may:

- add nodes
- remove nodes
- split nodes
- merge nodes
- change dependencies

when new information becomes available during execution.

---

## Completion

An Execution Graph is complete when:

- all required nodes are completed
- all approvals are resolved
- all validations are passed
- memory updates are recorded
- final results are produced
