# Context Assembly Model

## Definition

Context Assembly is the process of selecting and preparing context for agent execution.

## Purpose

Agents should receive relevant context, not all available information.

## Context Sources

Context may be assembled from:

- Work Item
- Product
- Repository
- Environment
- Memory
- Artifacts
- Execution Graph
- Policies
- Previous Runs

## Assembly Flow

Execution Request
→ Context Assembly
→ Context Package
→ Agent Execution

## Context Package

A Context Package may contain:

- objectives
- requirements
- relevant files
- architecture decisions
- previous artifacts
- memory records
- constraints
- policies

## Rules

Context should be relevant.

Context should be minimal.

Context should be traceable.

Sensitive context requires permission.

The Orchestrator owns Context Assembly.
