# System Architecture

The system is an orchestrator of specialized agents.

Users interact with the Orchestrator.

The Orchestrator:

- receives requests
- builds execution graphs
- selects agents
- manages context
- stores memory
- manages approvals
- tracks execution state

Agents do not interact directly with users.

Agents perform specialized work and report results back to the Orchestrator.
