# Agentic Dev Platform Checkpoint

Version: v0.39

## Current State

The platform is now structured around:

- CLI control plane
- product config plane
- backlog/task plane
- acceptance plane
- deployment/release verification plane
- agent runtime plane
- dynamic and multi-agent graph execution

## Main Runtime

Primary agent runtime:

orchestrator/agent_runtime/

Legacy agent runtime:

orchestrator/agents/

The legacy runtime is isolated and should not be used for new work.

## Key Commands

python3 agentic.py help
python3 agentic.py agents
python3 agentic.py dynamic-agent-graph "UI change on Sources page" --product rss-agent-lab_2 --dry-run
python3 agentic.py multi-agent-graph "Fan-out smoke" --product rss-agent-lab_2 --dry-run
python3 agentic.py ready
python3 agentic.py status --all

## Hardcoded / Not Yet Production-grade

- dynamic graph planner is keyword-based
- review agent is still mostly placeholder
- acceptance agent in new runtime is not fully wired to acceptance subsystem
- implementation lane agents create lane plans but do not write code yet
- recovery loop is not fully connected to agent graph execution
- memory exists but is lightly integrated
- external runtime state foundation exists but not all modules use it yet

## Next Target

v0.40 should focus on real acceptance/review runtime agents or runtime state migration.
