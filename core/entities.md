
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
