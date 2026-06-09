# Resource Model

## Definition

Resources are limited execution capacities used by the platform.

## Purpose

The platform must control cost, time and compute usage.

## Resource Types

- model tokens
- model cost
- API calls
- tool executions
- runtime duration
- compute resources
- storage

## Resource Limits

Limits may apply to:

- Product
- Work Item
- Execution Graph
- Agent Execution
- Tool Execution
- User

## Budget Fields

Each budget may define:

- max_cost
- max_tokens
- max_runtime
- max_tool_calls
- max_retries

## Rules

Resource usage must be tracked.

Executions must stop or request approval when limits are exceeded.

High-cost actions require approval.

Resource usage must be recorded in execution history.
