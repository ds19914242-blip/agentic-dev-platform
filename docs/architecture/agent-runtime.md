# Agent Runtime

## Goal

Move from pipeline-centric execution to agent-centric execution.

Current:

Task
  ->
Pipeline Runner
  ->
Implementation
  ->
Validation
  ->
Review

Target:

Task
  ->
Agent Graph
  ->
Agents
  ->
Artifacts

## Agent Interface

Every agent should implement:

class Agent:
    def run(self, context):
        pass

Output:

- status
- artifacts
- findings
- confidence
- handoff

## Core Agents

ArchitectAgent

Responsibilities:
- understand request
- decompose work
- define acceptance criteria

ImplementationAgent

Responsibilities:
- implement changes
- produce artifacts

ValidationAgent

Responsibilities:
- execute validators
- produce validation evidence

ReviewAgent

Responsibilities:
- inspect implementation
- identify risks

AcceptanceAgent

Responsibilities:
- execute acceptance scenarios
- verify outcome

ReleaseAgent

Responsibilities:
- verify production deployment
- confirm release

## Agent Graph

Initial graph:

Architect
  ->
Implementation
  ->
Validation
  ->
Review
  ->
Acceptance
  ->
Release

Future graph:

Architect
  ->
Task Split
  ->
Implementation A
Implementation B
Implementation C
  ->
Validation
  ->
Review
  ->
Acceptance
  ->
Release

## Agent Result

AgentResult

Fields:

- status
- confidence
- artifacts
- findings
- handoff

## Runtime Responsibilities

Agent Runtime should:

- execute agents
- persist results
- manage handoffs
- manage graph execution
- support parallel agents

Pipeline Runner becomes a compatibility layer on top of Agent Runtime.
