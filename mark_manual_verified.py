import argparse

from orchestrator.services.verification_service import mark_manual_verification


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path")
    parser.add_argument("--failed", action="store_true")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    try:
        result = mark_manual_verification(
            args.task_path,
            failed=args.failed,
            note=args.note,
        )
    except FileNotFoundError as exc:
        raise SystemExit(str(exc))

    task_path = result["task_path"]
    status = result["status"]
    bug_task = result["bug_task"]

    print(f"{task_path} marked {status}")

    product_outcome = result.get("product_outcome")

    if product_outcome:
        md_path, json_path = product_outcome
        print(f"Product outcome written: {md_path}")
        print(f"Product outcome JSON: {json_path}")

    if bug_task:
        print(f"Bug task created: {bug_task}")
        print("Run it with:")
        print(f"python3 run_backlog_task.py {bug_task}")


if __name__ == "__main__":
    main()
