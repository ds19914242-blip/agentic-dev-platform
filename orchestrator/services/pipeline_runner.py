import json
import os
from pathlib import Path

from orchestrator.llm_metrics import finish_metrics, start_metrics
from orchestrator.product_registry import load_product_config
from orchestrator.repository_state import ensure_clean_repo
from orchestrator.run_context import update_run_context
from orchestrator.run_manager import make_run_dir
from orchestrator.run_runtime import RunRuntime
from orchestrator.services.pipeline_stages import (
    run_implementation_stage,
    run_pull_request_stage,
    run_review_stage,
    run_validation_stage,
)


def _add_pipeline_graph_nodes(graph, pipeline):
    for node_id, name in [
        ("implementation", f"Run {pipeline} implementation"),
        ("validation", "Run validation"),
        ("review", "Run lightweight review"),
        ("pr", "Create pull request"),
    ]:
        graph.add(node_id, name)

    graph.write()


def _write_task_profile(run, run_dir, pipeline, task_path):
    profile = {
        "pipeline": pipeline,
        "task_file": str(task_path),
    }

    (run_dir / "task-profile.json").write_text(
        json.dumps(profile, indent=2, ensure_ascii=False)
    )
    run.artifact("task-profile.json", stage="implementation")


def _create_run(product_name, task_text, pipeline):
    run_dir = make_run_dir(pipeline.replace("_", "-"))
    run = RunRuntime(
        run_dir,
        product=product_name,
        request=task_text,
        run_type=pipeline,
    )

    return run_dir, run


def run_pipeline(
    product_name,
    task_path,
    pipeline,
    prompt,
    response_filename,
    prompt_filename,
    review_title,
    review,
    max_turns,
    repo_override=None,
):
    task_path = Path(task_path)
    task_text = task_path.read_text(errors="ignore")

    product = load_product_config(product_name)
    repo_path = repo_override or os.environ.get("AGENTIC_REPO_PATH_OVERRIDE") or product["repo_path"]
    product["repo_path"] = repo_path

    ensure_clean_repo(repo_path)

    run_dir, run = _create_run(product_name, task_text, pipeline)
    graph = run.graph

    _add_pipeline_graph_nodes(graph, pipeline)

    start_metrics(run_dir)
    os.environ["AGENTIC_RUN_DIR"] = str(run_dir)

    run.status("created")
    run.event(f"{pipeline} run created")

    update_run_context(
        run_dir,
        product=product_name,
        repo_path=repo_path,
        task_file=str(task_path),
        pipeline=pipeline,
    )

    _write_task_profile(run, run_dir, pipeline, task_path)

    run_implementation_stage(
        run=run,
        graph=graph,
        run_dir=run_dir,
        repo_path=repo_path,
        pipeline=pipeline,
        prompt=prompt,
        prompt_filename=prompt_filename,
        response_filename=response_filename,
        review_title=review_title,
        max_turns=max_turns,
    )

    validation_ok = run_validation_stage(
        run=run,
        graph=graph,
        run_dir=run_dir,
        repo_path=repo_path,
        product=product,
        task_path=task_path,
    )

    run_review_stage(
        run=run,
        graph=graph,
        run_dir=run_dir,
        review_title=review_title,
        review=review,
    )

    run_pull_request_stage(
        run=run,
        graph=graph,
        run_dir=run_dir,
        repo_path=repo_path,
        task_text=task_text,
        pipeline=pipeline,
    )

    finish_metrics(run_dir)

    print(f"Run: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")

    pull_request_path = run_dir / "pull-request.md"
    if pull_request_path.exists():
        print(pull_request_path.read_text())
