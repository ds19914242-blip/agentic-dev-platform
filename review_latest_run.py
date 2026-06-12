# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.post_run_review import create_post_run_review
from orchestrator.run_status import append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    product_name = input("Product name: ").strip()

    product = load_product_config(product_name)
    run_dir = latest_run()

    path = create_post_run_review(run_dir, product["repo_path"])
    append_event(run_dir, "Post run review created")

    print(f"Post run review saved to: {path}")


if __name__ == "__main__":
    main()
