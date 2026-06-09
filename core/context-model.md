# Context Model

## Definition

Context is the information provided to agents before execution.

Agents do not decide their own context.

The Orchestrator builds and provides context.

## Context Sources

Context may include:

- Work Item details
- repository structure
- relevant files
- product memory
- previous decisions
- execution history
- environment information
- policies
- approvals

## Context Types

### System Context

Rules and architecture of the platform.

### Work Item Context

Information about the current request.

### Repository Context

Relevant code, files and dependencies.

### Product Context

Business logic, users and product goals.

### Memory Context

Past decisions, bugs, releases and lessons.

## Rules

Context must be relevant, minimal and traceable.

Agents should receive only the context needed for their work.

Sensitive context requires permission.
