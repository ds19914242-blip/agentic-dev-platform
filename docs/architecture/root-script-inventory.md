# Root Script Inventory

The platform currently has many root-level Python scripts.

Long-term target: keep only `agentic.py` in the repository root.

## Keep in root

- agentic.py

## Active CLI scripts

These are currently routed from `agentic.py` through `orchestrator/application/command_registry.py`.

- approve_feature_spec.py
- approve_product_spec.py
- backlog_dag.py
- backlog_parallel_worktree.py
- backlog_ready.py
- backlog_scheduler.py
- backlog_status.py
- classify_task.py
- decompose_feature.py
- mark_manual_verified.py
- memory_report.py
- run_acceptance.py
- run_acceptance_scenarios.py
- run_acceptance_status.py
- run_agent.py
- run_agent_registry.py
- run_autonomous_feature.py
- run_backlog_task.py
- run_deployment_verification.py
- sync_backlog_prs.py
- agentic_metrics.py

## Legacy scripts

These should not be used for new platform workflows.

- approve_latest_plan.py
- confidence_latest_run.py
- create_pr_latest_run.py
- execute_latest_run.py
- implement_latest_plan.py
- review_latest_run.py
- validate_latest_run.py
- run_fast_task.py
- run_standard_task.py
- run_epic_task.py
- run_feature.py
- feature_request_runner.py
- planner.py
- main.py

## Internal/dev utilities

- claude_prompt_builder.py
- record_claude_response.py
- record_result.py
- backlog_parallel.py

## Refactoring direction

Phase 1:

- keep scripts where they are
- document ownership
- stop adding new root scripts except temporary wrappers

Phase 2:

- move active commands to `cli/commands/`
- keep thin compatibility wrappers in root

Phase 3:

- remove legacy latest-run commands
- move internal utilities to `tools/`
