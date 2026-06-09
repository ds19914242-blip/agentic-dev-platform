# Agent Registry Model

## Definition

The Agent Registry is the catalog of all agents available to the system.

The Orchestrator selects agents from the Agent Registry.

## Purpose

The Agent Registry provides a single source of truth for agent capabilities and availability.

## Agent Record

Each registered agent must define:

- id
- name
- version
- type
- description
- model
- capabilities
- allowed_tools
- permissions
- supported_workflows
- status

## Agent Status

- active
- disabled
- deprecated
- experimental

## Agent Selection

The Orchestrator selects agents based on:

- workflow requirements
- capabilities
- permissions
- tool requirements
- risk level

## Rules

Only registered agents may participate in execution.

Agent versions must be tracked.

Agent changes must be auditable.
