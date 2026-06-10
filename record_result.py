from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.execution_result import record_execution_result


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    product_name = input("Product name: ").strip()
    summary = input("Implementation summary: ").strip()

    product = load_product_config(product_name)
    run_dir = latest_run()

    record_execution_result(
        run_dir=run_dir,
        repo_path=product["repo_path"],
        summary=summary,
    )

    print(f"Recorded execution result in: {run_dir / 'implementation.md'}")


if __name__ == "__main__":
    main()
