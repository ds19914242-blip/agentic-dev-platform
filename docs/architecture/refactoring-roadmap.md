# Refactoring Roadmap

Batch 1:

Introduce normalized backlog/task layer.

Files:

- orchestrator/task_status.py
- orchestrator/task_model.py
- orchestrator/backlog_store.py
- backlog_status.py

Batch 2:

Document current architecture and dependency map.

Files:

- docs/architecture/current-architecture.md
- docs/architecture/refactoring-roadmap.md
- scripts/import_inventory.py

Batch 3:

Migrate read-only backlog commands to backlog_store.

Candidates:

- backlog_ready.py
- backlog_dag.py

Avoid first:

- run_backlog_task.py
- mark_manual_verified.py
- approve_feature_spec.py
- decompose_feature.py

Batch 4:

Extract verification service.

Target:

- orchestrator/services/verification_service.py

Batch 5:

Extract task execution service.

Target:

- orchestrator/services/task_execution_service.py

Batch 6:

Add product verification adapter.

Target:

- orchestrator/verification/product_verification.py
- orchestrator/verification/verification_result.py

Batch 7:

Add browser acceptance execution.

Target:

- Playwright-based acceptance runner
- scenario parser
- result writer

Batch 8:

Unify recovery tasks.

Sources:

- manual verification failed
- E2E failed
- validation failed
- reviewer failed
- merge conflict detected

Target:

failure -> recovery task -> backlog -> normal execution

Batch 9:

Deprecate old latest-run workflow after usage check.
