
def route_task(task_profile):
    pipeline = task_profile.get("pipeline") or "standard"

    if pipeline not in {"fast", "standard_bugfix", "standard", "full", "audit"}:
        return "standard"

    return pipeline


def pipeline_description(pipeline):
    return {
        "fast": "implement -> validate -> review -> PR",
        "standard_bugfix": "root cause -> fix -> validate -> review -> PR",
        "standard": "light plan -> implement -> validate -> review -> PR",
        "full": "plan -> architecture -> QA -> implement -> validate -> review -> confidence -> PR",
        "audit": "scan -> findings -> follow-up tasks",
    }.get(pipeline, "standard")
