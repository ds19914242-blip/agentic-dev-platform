# Scheduling Model

## Definition

Scheduling is the process of deciding when and in what order work is executed.

## Purpose

The platform must allocate resources across multiple products, work items and execution graphs.

## Scheduling Objects

The Scheduler manages:

- Products
- Work Items
- Execution Graphs
- Nodes
- Agent Executions
- Tool Executions

## Scheduling Factors

Scheduling may consider:

- priority
- risk level
- deadlines
- dependencies
- resource availability
- cost limits
- approval status

## Priority Levels

- critical
- high
- normal
- low

## Parallel Execution

Independent work may run in parallel.

Dependent work must wait for prerequisites.

## Rules

Higher priority work should be scheduled first.

Blocked work must not consume resources.

Approval-gated work must pause until approval is resolved.

Scheduling decisions must be recorded.
