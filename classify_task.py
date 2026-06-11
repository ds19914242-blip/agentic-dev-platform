import json
import sys

from orchestrator.product_registry import load_product_config
from orchestrator.task_classifier import classify_task
from orchestrator.execution_router import pipeline_description


def main():
    product_name = sys.argv[1] if len(sys.argv) > 2 else "rss-agent-lab_2"
    task_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else " ".join(sys.argv[1:])

    if not task_text:
        raise SystemExit("Usage: python3 classify_task.py [product] <task text>")

    product = load_product_config(product_name)
    profile = classify_task(product["repo_path"], task_text)

    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print()
    print("Pipeline:", pipeline_description(profile["pipeline"]))


if __name__ == "__main__":
    main()
