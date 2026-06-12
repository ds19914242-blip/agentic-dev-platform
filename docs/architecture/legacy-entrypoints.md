# Legacy Entrypoints

These files appear to belong to older workflows.

Do not delete them until runtime usage is confirmed.

## Latest-run workflow candidates

- approve_latest_plan.py
- create_pr_latest_run.py
- confidence_latest_run.py
- execute_latest_run.py
- implement_latest_plan.py
- review_latest_run.py
- validate_latest_run.py
- record_result.py
- record_claude_response.py

## Older workflow candidates

- run_feature.py
- main.py
- planner.py
- classify_task.py
- feature_request_runner.py
- run_epic_task.py

## Deletion rule

Before deleting any legacy entrypoint:

1. Check imports.
2. Check agentic.py command routing.
3. Check docs and README references.
4. Deprecate first.
5. Delete only after one stable release.

## Current usage findings

Generated from grep/import inventory.

### Still routed

- `validate_latest_run.py` is still routed from `agentic.py` through the `validate` command.

### Used by current execution

- `run_fast_task.py` is used by `orchestrator/services/task_execution_service.py`
- `run_standard_task.py` is used by `orchestrator/services/task_execution_service.py`
- `run_autonomous_feature.py` is used by:
  - `agentic.py`
  - `run_epic_task.py`
  - `orchestrator/services/task_execution_service.py`

### Legacy candidates with no active command routing found

- `approve_latest_plan.py`
- `execute_latest_run.py`
- `review_latest_run.py`

These should remain documented but should not be extended.

