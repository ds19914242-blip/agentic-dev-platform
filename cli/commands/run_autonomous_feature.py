from orchestrator.workflows.autonomous_workflow import run_autonomous_workflow


def main():
    product_name = input("Product name: ").strip()
    feature = input("Feature request: ").strip()

    run_autonomous_workflow(product_name, feature)


if __name__ == "__main__":
    main()
