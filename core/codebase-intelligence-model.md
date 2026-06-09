# Codebase Intelligence Model

## Definition

Codebase Intelligence is the system's understanding of a repository.

## Purpose

Agents need structured knowledge of codebases before modifying them.

## Codebase Map

A Codebase Map may include:

- directory structure
- modules
- services
- APIs
- database models
- dependencies
- tests
- configuration files
- entry points
- critical flows

## Flow

Repository
→ Codebase Analysis
→ Codebase Map
→ Context Assembly
→ Agent Execution

## Rules

Agents should not modify code without relevant codebase context.

Codebase Maps must be updated after major changes.

Important codebase knowledge should be stored in memory.
