import os

from orchestrator.complexity_classifier import classify_request_with_llm, parse_complexity
from orchestrator.product_registry import load_product_config
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.repository_scanner import scan_repo
from orchestrator.work_item_analyst import analyze_work_item


def prepare_autonomous_run(product_name, feature):
    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    repo_path_override = os.environ.get("AGENTIC_REPO_PATH_OVERRIDE")
    if repo_path_override:
        repo_path = repo_path_override
        product["repo_path"] = repo_path_override

    files_for_classification = scan_repo(repo_path)
    repo_map_for_classification = format_repository_map(
        build_repository_map(files_for_classification)
    )

    work_item = analyze_work_item(repo_path, feature)

    classification_text = classify_request_with_llm(
        repo_path,
        feature,
        repo_map_for_classification,
    )

    classification = parse_complexity(classification_text)

    if work_item.get("should_decompose"):
        classification["route"] = "DECOMPOSE_FIRST"

    human_approved = os.environ.get("AGENTIC_HUMAN_APPROVED") == "1"

    if human_approved and (
        classification.get("route") == "NEEDS_HUMAN_REVIEW"
        or "NEEDS_HUMAN_REVIEW" in classification_text
    ):
        classification["route"] = "RUN_AUTONOMOUSLY"

    return {
        "product": product,
        "repo_path": repo_path,
        "work_item": work_item,
        "classification": classification,
        "classification_text": classification_text,
    }
