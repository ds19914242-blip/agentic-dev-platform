
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
