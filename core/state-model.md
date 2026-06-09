# State Model

## Definition

State is the current condition of system objects during execution.

The system must track state for Work Items, Execution Graphs, Nodes, Agents, Tools and Approvals.

## State Ownership

The Orchestrator owns execution state.

Agents report state changes, but do not own state.

## State Types

### Work Item State

Tracks overall progress of a request.

### Execution Graph State

Tracks graph-level execution progress.

### Node State

Tracks individual execution units.

### Agent State

Tracks agent availability and current execution status.

### Tool State

Tracks tool requests and results.

### Approval State

Tracks human decisions.

## Rules

All state changes must be recorded.

State transitions must be traceable.

Failed states must include errors and recovery options.

The system must be able to resume from stored state when possible.
