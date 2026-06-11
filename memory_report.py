import sys
from pathlib import Path

from orchestrator.memory_store import (
    load_product_memory,
    load_run_memory,
    load_architecture_memory,
)
from orchestrator.failure_memory import load_failure_memory


def main():
    product = sys.argv[1] if len(sys.argv) > 1 else "rss-agent-lab_2"

    product_memory = load_product_memory(product)
    run_memory = load_run_memory(product)
    architecture_memory = load_architecture_memory(product)
    failure_memory = load_failure_memory(product)

    print(f"Product: {product}")
    print()
    print(f"Product memory keys: {', '.join(product_memory.keys()) or 'none'}")
    print(f"Run memory entries: {len(run_memory)}")
    print(f"Architecture decisions: {len(architecture_memory)}")
    print(f"Failure memory entries: {len(failure_memory)}")

    if failure_memory:
        print()
        print("Recent failures:")
        for failure in failure_memory[-5:]:
            print(f"- {failure.get('run_id')}: {failure.get('failure_type')} — {failure.get('request')}")


if __name__ == "__main__":
    main()
