# Agentic Dev Platform Map

This document describes the current platform shape.

## CLI Plane

agentic.py
  -> orchestrator/application/command_registry.py
  -> cli/commands/*
  -> cli/legacy/*

Rule:
New commands go to cli/commands.

## Product Plane

products/<product>/config.yaml

Loader:
orchestrator/product_registry.py

Contains:
- repo_path
- framework
- capabilities
- validators
- acceptance
- deployment

## Backlog Plane

backlog/<epic>/task-XXX.md

Core modules:
- orchestrator/backlog_store.py
- orchestrator/backlog_query.py
- orchestrator/backlog_dag.py
- orchestrator/task_status.py

Commands:
- agentic.py status
- agentic.py ready
- agentic.py dag
- agentic.py backlog

## Runtime Plane

Runtime-generated state:

- runs/
- backlog/
- evidence/

Target direction:

agentic-dev-platform/
  source code

agentic-dev-data/
  runs/
  backlog/
  evidence/

## Pipeline Plane

Main service:

orchestrator/services/pipeline_runner.py

Stages:

- implementation
- validation
- review
- pull_request

Stage implementations:

orchestrator/services/pipeline_stages.py

## Acceptance Plane

orchestrator/acceptance/

Responsibilities:

- scenario parsing
- playwright generation
- acceptance execution
- bug recovery

Commands:

- agentic.py acceptance
- agentic.py acceptance-status
- agentic.py acceptance-scenarios

## Release Plane

orchestrator/deployment/

Command:

agentic.py release-check

Outputs:

- release-verification.md
- release-verification.json

Statuses:

- production_verification_running
- release_confirmed
- release_failed

## Agent Plane

Core modules:

- orchestrator/claude_executor.py
- orchestrator/agent_context.py

Commands:

- agentic.py agent
- agentic.py agents

## Legacy Plane

Legacy scripts:

cli/legacy/

Compatibility only.

## Target Architecture

agentic.py
  -> command registry
     -> cli commands
        -> services
           -> domain modules
              -> storage

Platform = control plane

Product repos = work planes
