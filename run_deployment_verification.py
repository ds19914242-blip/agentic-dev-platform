import argparse

from orchestrator.deployment.production_verifier import verify_production_release


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path")
    parser.add_argument("--product", required=True)
    args = parser.parse_args()

    result = verify_production_release(
        task_path=args.task_path,
        product_name=args.product,
    )

    print(f"Production URL: {result['production_url']}")
    print(f"Release verification: {'passed' if result['passed'] else 'failed'}")
    print(f"Markdown: {result['release_markdown']}")
    print(f"JSON: {result['release_json']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
