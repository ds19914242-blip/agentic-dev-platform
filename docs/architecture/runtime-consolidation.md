# Runtime Consolidation

## Decision

`orchestrator/agent_runtime/` is the primary Agent Runtime.

`orchestrator/agents/` is legacy and should not be used for new workflows.

## Current source of truth

- Agent
- AgentContext
- AgentResult
- AgentGraph
- AgentGraphExecutor
- AgentRegistry
- builtin runtime agents

## Legacy layer

`orchestrator/agents/` contains older runtime definitions and YAML-based agent metadata.

It remains in the repository for compatibility only.

## Migration rule

New agent work must go to:

orchestrator/agent_runtime/

Do not add new runtime logic to:

orchestrator/agents/

## Known hardcoded parts

- static multi-agent graph
- keyword-based dynamic graph planner
- placeholder review agent
- placeholder acceptance agent
- lane agents plan work but do not implement code yet
- recovery loop is not wired into graph execution
- memory exists but is not deeply integrated
