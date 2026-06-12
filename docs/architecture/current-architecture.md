# Current Architecture

agentic-dev-platform is a file-based agentic development platform.

Main flow:

agentic.py epic
  -> decompose_feature.py
  -> feature-spec.md
  -> human review

agentic.py approve-spec
  -> approve_feature_spec.py
  -> acceptance-scenarios.md
  -> task-001.md ... task-N.md
  -> final E2E verification task

agentic.py backlog <task.md>
  -> run_backlog_task.py
  -> fast / standard / autonomous pipeline
  -> validation
  -> PR or manual verification

agentic.py verify <task.md>
  -> mark_manual_verified.py
  -> passed / failed
  -> failed creates bug task

Production entrypoints:

- agentic.py
- decompose_feature.py
- approve_feature_spec.py
- run_backlog_task.py
- run_fast_task.py
- run_standard_task.py
- run_autonomous_feature.py
- mark_manual_verified.py

Backlog utilities:

- backlog_status.py
- backlog_ready.py
- backlog_dag.py
- backlog_scheduler.py
- backlog_parallel.py
- backlog_parallel_worktree.py
- sync_backlog_prs.py

New normalized backlog layer:

- orchestrator/task_status.py
- orchestrator/task_model.py
- orchestrator/backlog_store.py

Legacy/latest-run candidates:

- approve_latest_plan.py
- create_pr_latest_run.py
- confidence_latest_run.py
- execute_latest_run.py
- implement_latest_plan.py
- review_latest_run.py
- validate_latest_run.py
- record_result.py
- record_claude_response.py

Current issue:

The platform currently has two overlapping styles:

- top-level workflow scripts
- orchestrator package modules

Target direction:

agentic.py -> thin CLI
orchestrator/services/* -> workflow logic
orchestrator/state/* -> storage access
orchestrator/execution/* -> execution pipelines

## Service layer

The platform now has an initial application service layer:

- `orchestrator/services/verification_service.py`
- `orchestrator/services/task_execution_service.py`

Thin CLI entrypoints:

- `mark_manual_verified.py`
- `run_backlog_task.py`

These scripts now mainly parse CLI arguments and delegate workflow logic to services.

