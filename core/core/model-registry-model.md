# Model Registry Model

## Definition

The Model Registry is the catalog of AI models available to the platform.

Agents are not tied to specific models.

Agents define requirements.

The Orchestrator selects models from the Model Registry.

## Principle

Agent is a role.

Model is an execution engine.

Agent ≠ Model.

## Model Record

Each model must define:

- id
- provider
- name
- version
- capabilities
- context_window
- cost_profile
- latency_profile
- reliability_profile
- supported_tools
- risk_level_allowed
- status

## Agent Requirements

Agents may define requirements such as:

- reasoning_level
- context_size
- tool_usage
- speed
- cost_limit
- reliability_level

## Selection Flow

Agent Requirements
→ Orchestrator
→ Model Registry
→ Model Selection
→ Agent Execution

## Rules

Models must be swappable.

Model selection must be recorded.

High-risk executions may require stronger models.

Agents must not select their own models.

The platform should support multiple model providers.
