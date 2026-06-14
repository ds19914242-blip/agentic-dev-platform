from pathlib import Path


def build_runtime_analysis_context(task, repo_path=""):
    context = {
        "task": task,
        "repo_path": repo_path,
        "available": {},
        "summary": [],
    }

    try:
        from orchestrator.repository_scanner import scan_repository

        if repo_path:
            scan = scan_repository(repo_path)
            context["available"]["repository_scanner"] = True
            context["repository_scan"] = scan
            context["summary"].append("repository_scanner available")
    except Exception as exc:
        context["available"]["repository_scanner"] = False
        context["summary"].append(f"repository_scanner unavailable: {exc}")

    try:
        from orchestrator.affected_file_detector import detect_affected_files

        if repo_path:
            affected = detect_affected_files(repo_path, task)
            context["available"]["affected_file_detector"] = True
            context["affected_files"] = affected
            context["summary"].append("affected_file_detector available")
    except Exception as exc:
        context["available"]["affected_file_detector"] = False
        context["summary"].append(f"affected_file_detector unavailable: {exc}")

    try:
        from orchestrator.work_item_analyst import analyze_work_item

        analysis = analyze_work_item(task)
        context["available"]["work_item_analyst"] = True
        context["work_item_analysis"] = analysis
        context["summary"].append("work_item_analyst available")
    except Exception as exc:
        context["available"]["work_item_analyst"] = False
        context["summary"].append(f"work_item_analyst unavailable: {exc}")

    return context
