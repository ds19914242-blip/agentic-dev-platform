import os

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
