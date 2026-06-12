import os

from orchestrator.context_builder import read_context
from orchestrator.affected_file_detector import detect_affected_files
from orchestrator.import_analyzer import analyze_imports, format_import_map
from orchestrator.planner_selected_files import extract_files_from_plan, write_planner_selected_files
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.repository_intelligence_v2 import rank_affected_files
from orchestrator.repository_scanner import scan_repo

from orchestrator.context_curator import write_memory_context
from orchestrator.llm_metrics import start_metrics
from orchestrator.memory_store import update_product_memory
from orchestrator.run_context import update_run_context
from orchestrator.run_manager import make_run_dir
from orchestrator.run_runtime import RunRuntime


def create_autonomous_run(product_name, product, repo_path, feature, work_item):
    run_dir = make_run_dir("feature")

    run = RunRuntime(
        run_dir,
        product=product_name,
        request=feature,
        run_type="feature",
    )
    graph_v2 = run.graph

    start_metrics(run_dir)
    os.environ["AGENTIC_RUN_DIR"] = str(run_dir)
    run.status("created")
    run.event("Autonomous feature run created")
    update_run_context(
        run_dir,
        product=product_name,
        repo_path=repo_path,
        feature=feature,
        work_item=work_item,
    )

    update_product_memory(product_name, {
        "name": product.get("name", product_name),
        "repo_path": repo_path,
        "type": product.get("type"),
        "status": product.get("status"),
        "framework": product.get("framework"),
        "capabilities": product.get("capabilities", {}),
        "validators": product.get("validators", []),
    })

    memory_context_path, memory_context = write_memory_context(
        run_dir=run_dir,
        product_name=product_name,
        feature=feature,
    )

    return {
        "run_dir": run_dir,
        "run": run,
        "graph_v2": graph_v2,
        "memory_context_path": memory_context_path,
        "memory_context": memory_context,
    }


def initialize_autonomous_graph(graph_v2):
    for node_id, name in [
        ("repo_state", "Check clean repository"),
        ("repo_scan", "Scan repository"),
        ("repo_intelligence", "Build repository intelligence"),
        ("affected_files", "Detect affected files"),
        ("planning", "Create plan"),
        ("architecture", "Create architecture review"),
        ("qa", "Create QA plan"),
        ("security", "Run security gate"),
        ("claude_plan", "Run Claude planning"),
        ("approved_plan", "Approve plan"),
        ("implementation", "Run Claude implementation"),
        ("validation", "Run validation"),
        ("replanning", "Replan after validation failure"),
        ("review", "Run reviewer agent"),
        ("post_review", "Create post-run review"),
        ("acceptance", "Run acceptance gate"),
        ("confidence", "Run confidence gate"),
    ]:
        graph_v2.add(node_id, name)

    graph_v2.complete("repo_state")
    graph_v2.write()


def prepare_repository_context(repo_path, feature, memory_context):
    files = scan_repo(repo_path)
    repo_map = build_repository_map(files)
    repo_map_text = format_repository_map(repo_map)

    import_map = analyze_imports(repo_path, files)
    import_map_text = format_import_map(import_map)

    affected = rank_affected_files(feature, files) or detect_affected_files(feature, files)
    context = read_context(repo_path, affected)
    context = context + "\n\n" + memory_context

    return {
        "files": files,
        "repo_map": repo_map,
        "repo_map_text": repo_map_text,
        "import_map": import_map,
        "import_map_text": import_map_text,
        "affected": affected,
        "context": context,
    }


def apply_planner_selected_files(run_dir, plan, files, affected, run):
    planner_selected_files = extract_files_from_plan(plan, files)
    if planner_selected_files:
        affected = planner_selected_files

    write_planner_selected_files(run_dir, planner_selected_files)
    run.artifact("planner-selected-files.md", stage="planning")

    return affected, planner_selected_files
