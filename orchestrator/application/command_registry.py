COMMANDS = {
    "feature": {
        "script": "run_autonomous_feature.py",
        "description": "Run one autonomous feature",
        "legacy": False,
    },
    "decompose": {
        "script": "decompose_feature.py",
        "description": "Decompose a large request into backlog tasks",
        "legacy": False,
    },
    "backlog": {
        "script": "run_backlog_task.py",
        "description": "Run a backlog task",
        "legacy": False,
    },
    "status": {
        "script": "backlog_status.py",
        "description": "Show backlog status",
        "legacy": False,
    },
    "sync": {
        "script": "sync_backlog_prs.py",
        "description": "Sync backlog PR statuses",
        "legacy": False,
    },
    "dag": {
        "script": "backlog_dag.py",
        "description": "Show dependency-aware backlog DAG",
        "legacy": False,
    },
    "ready": {
        "script": "backlog_ready.py",
        "description": "Show ready backlog tasks",
        "legacy": False,
    },
    "schedule": {
        "script": "backlog_scheduler.py",
        "description": "Run next dependency-ready backlog task",
        "legacy": False,
    },
    "parallel": {
        "script": "backlog_parallel_worktree.py",
        "description": "Run ready backlog tasks in parallel",
        "legacy": False,
    },
    "memory": {
        "script": "memory_report.py",
        "description": "Show product memory report",
        "legacy": False,
    },
    "classify": {
        "script": "classify_task.py",
        "description": "Classify a task and show selected pipeline",
        "legacy": False,
    },
    "metrics": {
        "script": "agentic_metrics.py",
        "description": "Show runtime metrics",
        "legacy": False,
    },
    "approve-spec": {
        "script": "approve_feature_spec.py",
        "description": "Approve feature spec and generate backlog tasks",
        "legacy": False,
    },
    "approve-product-spec": {
        "script": "approve_product_spec.py",
        "description": "Approve product spec and generate feature spec",
        "legacy": False,
    },
    "verify": {
        "script": "mark_manual_verified.py",
        "description": "Mark manual verification passed/failed",
        "legacy": False,
    },
    "acceptance": {
        "script": "run_acceptance.py",
        "description": "Run acceptance verification or generated Playwright tests for an epic",
        "legacy": False,
    },
    "release-check": {
        "script": "run_deployment_verification.py",
        "description": "Verify production deployment and confirm release",
        "legacy": False,
    },
    "acceptance-status": {
        "script": "run_acceptance_status.py",
        "description": "Show latest acceptance verification result",
        "legacy": False,
    },
    "acceptance-scenarios": {
        "script": "run_acceptance_scenarios.py",
        "description": "Parse acceptance scenarios for an epic",
        "legacy": False,
    },
    "agent": {
        "script": "run_agent.py",
        "description": "Run an agent through Agent Runtime",
        "legacy": False,
    },
    "agents": {
        "script": "run_agent_registry.py",
        "description": "List registered agents and definitions",
        "legacy": False,
    },
    "agent-graph": {
        "script": "run_agent_graph.py",
        "description": "Run the default agent graph",
        "legacy": False,
    },
    "multi-agent-graph": {
        "script": "run_multi_agent_graph.py",
        "description": "Run the fan-out/fan-in multi-agent graph",
        "legacy": False,
    },
    "validate": {
        "script": "validate_latest_run.py",
        "description": "Validate latest run",
        "legacy": True,
    },
    "confidence": {
        "script": "confidence_latest_run.py",
        "description": "Confidence report for latest run",
        "legacy": True,
    },
}


ALIASES = {
    "run": "feature",
    "epic": "decompose",
    "next": "schedule",
    "progress": "status",
}


def resolve_command(name):
    name = ALIASES.get(name, name)
    return COMMANDS.get(name)


def active_commands():
    return {
        name: meta
        for name, meta in COMMANDS.items()
        if not meta["legacy"]
    }


def legacy_commands():
    return {
        name: meta
        for name, meta in COMMANDS.items()
        if meta["legacy"]
    }
