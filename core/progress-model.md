# Progress Model

## Definition

Progress represents the current execution status of a Work Item, Product or Execution Graph.

## Purpose

Progress allows the system and humans to understand execution state and remaining work.

## Progress Levels

### Product Progress

Tracks overall product delivery progress.

### Work Item Progress

Tracks progress of a specific request.

### Execution Graph Progress

Tracks graph execution status.

### Task Progress

Tracks individual task completion.

## Progress Fields

Progress records may include:

- total_items
- completed_items
- failed_items
- blocked_items
- pending_items
- completion_percentage
- current_stage
- estimated_remaining_work

## Rules

Progress must be continuously updated.

Progress is owned by the Orchestrator.

Progress must be visible to humans.

Progress must be derived from actual execution state.
