# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.validation_runner import run_validators, write_validation_report
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(
        p for p in Path("runs").glob("feature-*")
        if p.is_dir()
    )

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    product_name = input("Product name: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]
    validators = product.get("validators", [])

    run_dir = latest_run()

    print(f"Validating run: {run_dir}")
    print(f"Using repo: {repo_path}")

    results = run_validators(repo_path, validators)
    validation_path, passed = write_validation_report(run_dir, results)

    if passed:
        write_status(run_dir, "validated")
        append_event(run_dir, "Validation passed")
    else:
        write_status(run_dir, "validation_failed")
        append_event(run_dir, "Validation failed")

    print(f"Validation {'passed' if passed else 'failed'}: {validation_path}")


if __name__ == "__main__":
    main()
