# Orchestrator Decomposition Model

## Definition

Orchestrator Decomposition splits the Orchestrator into internal subsystems.

## Purpose

The Orchestrator should not become a single overloaded god-object.

## Subsystems

### Request Intake

Receives and normalizes human requests.

### Work Item Manager

Creates and tracks Work Items.

### Workflow Selector

Selects Workflow Templates.

### Graph Planner

Creates and updates Execution Graphs.

### Scheduler

Decides execution order and timing.

### Runtime Controller

Runs, pauses, resumes and recovers executions.

### Context Manager

Builds Context Packages.

### Policy Engine

Evaluates permissions, risk and approvals.

### Tool Gateway

Controls all tool access.

### Memory Manager

Reads and writes memory.

### Artifact Manager

Stores and versions artifacts.

## Rule

The Orchestrator coordinates subsystems.

Subsystems handle specialized responsibilities.
