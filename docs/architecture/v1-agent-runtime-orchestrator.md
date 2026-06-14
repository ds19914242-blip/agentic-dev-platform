# v1.0 Agent Runtime Orchestrator

## What v1.0 means

This is an engineering milestone, not final product maturity.

The Agent Runtime is now able to act as an orchestrator:

- plan a graph dynamically
- execute graph nodes
- fan out into lanes
- collect artifacts
- run validation/review/acceptance/release agents
- expose a CLI command

## Main commands

python3 agentic.py runtime-orchestrator "task" --product rss-agent-lab_2

python3 agentic.py runtime-task backlog/<epic>/task-XXX.md --product rss-agent-lab_2

## Safe mode

By default, runtime-orchestrator and runtime-task run in dry-run mode.

Use --execute only when real validation, acceptance, or release execution is intended.

## What is real

- Agent model
- Agent registry
- Graph executor
- Dynamic graph planner
- Architect agent
- Lane agents
- Validation agent
- Review agent
- Acceptance agent adapter
- Release agent
- Runtime task command

## Still hardcoded

- dynamic planner is keyword-based
- implementation agents still prepare handoff rather than directly writing code
- recovery loop is not deeply integrated
- memory exists but is not strongly decision-driving yet

## Next after v1.0

- LLM planner
- real implementation agents that call Claude safely
- graph-level recovery loop
- stronger memory usage
