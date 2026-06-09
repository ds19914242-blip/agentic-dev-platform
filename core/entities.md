
# System Entities

## Orchestrator

Controls the entire system.

## Agent

Performs specialized work.

## Work Item

A request for work.

Examples:
- New Product
- Feature
- Bug Fix
- Refactor
- Research
- Release
- Incident

## Execution Graph

A dynamic graph of steps created by the Orchestrator for each Work Item.

It defines:
- what should be done
- which agents should work
- what can run in parallel
- what requires approval
- what result is expected

## Repository

A source code repository managed by the system.

Examples:
- GitHub repository
- Local repository

Repositories contain code that agents can analyze and modify.
## Environment

A runtime environment where a product can run.

Examples:
- local
- staging
- production

Agents must know which environment they are allowed to use or modify.

## Tool

An external capability used by an agent.

Examples:
- shell
- git
- GitHub
- Docker
- browser
- deployment platform

Tools are accessed through the Orchestrator, not directly by agents.

## Memory

Stored knowledge used by the system.

Examples:
- product decisions
- previous bugs
- architecture notes
- successful runs
- failed runs

Memory helps agents avoid starting from zero.

## Approval

A human decision required before risky actions.

Examples:
- deploy to production
- delete code
- change database schema
- modify secrets
- merge PR
