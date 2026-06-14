# Legacy Agent Isolation

## Decision

The active runtime is:

orchestrator/agent_runtime/

The old runtime is isolated in:

orchestrator/agents/

## Active command path

agentic.py
  -> command_registry
  -> cli/commands
  -> orchestrator/agent_runtime

## Legacy path

orchestrator/agents/

This package is retained only for historical compatibility and reference.

New features must not import:

orchestrator.agents.*

## Runtime bridge

Legacy-style service calls should use:

orchestrator/agent_runtime/compatibility/legacy_runtime.py

This keeps old call sites compatible while using the new runtime as the source of truth.
