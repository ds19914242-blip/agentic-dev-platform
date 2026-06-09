# Memory Model

## Principle

The system must not start from zero on every execution.

Memory stores knowledge across products, work items and agent runs.

## Memory Types

### Global Memory

Knowledge shared across the entire system.

Examples:
- coding standards
- architecture principles
- security policies

### Product Memory

Knowledge specific to a product.

Examples:
- architecture decisions
- business rules
- release history
- known issues

### Execution Memory

Knowledge generated during a specific Work Item.

Examples:
- findings
- plans
- decisions
- results

## Rules

Memory is owned by the Orchestrator.

Agents may read and update memory only through the Orchestrator.
