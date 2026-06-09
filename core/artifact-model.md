# Artifact Model

## Definition

An Artifact is an output produced during system execution.

Artifacts are used for review, memory, implementation and audit.

## Artifact Types

- product_spec
- technical_plan
- execution_graph
- code_patch
- pull_request
- test_report
- review_report
- security_report
- release_notes
- deployment_report
- decision_record
- incident_report

## Artifact Fields

Each Artifact must define:

- id
- type
- work_item_id
- created_by
- created_at
- source_node
- content
- status
- version

## Artifact Status

- draft
- proposed
- approved
- rejected
- superseded
- final

## Rules

Important agent outputs must be stored as Artifacts.

Artifacts must be linked to Work Items and Execution Graph nodes.

Final decisions must be stored as decision records.
