# Orchestrator Model

## Definition

The Orchestrator is the central control system of the platform.

It manages agents, tools, memory, approvals, context and execution graphs.

## Responsibilities

The Orchestrator:

- receives human requests
- creates Work Items
- builds Execution Graphs
- loads context
- selects agents
- assigns work
- manages tool access
- tracks execution state
- requests approvals
- records memory
- returns final results

## Orchestrator Does Not

The Orchestrator does not directly implement product features.

Implementation is performed by agents.

## Core Decisions

The Orchestrator decides:

- which agents to run
- what context to provide
- which tools are allowed
- when approval is required
- whether execution should continue, retry or stop
- when a Work Item is complete

## State Ownership

The Orchestrator owns execution state.

Agents return results but do not own platform state.

## Rules

Agents report to the Orchestrator.

Tools are accessed through the Orchestrator.

Memory is updated through the Orchestrator.

Approvals are requested by the Orchestrator.

The final result is delivered by the Orchestrator.
