from pathlib import Path


LEGACY_CANDIDATES = [
    "approve_latest_plan.py",
    "create_pr_latest_run.py",
    "confidence_latest_run.py",
    "execute_latest_run.py",
    "implement_latest_plan.py",
    "review_latest_run.py",
    "validate_latest_run.py",
    "record_result.py",
    "record_claude_response.py",
    "run_feature.py",
    "main.py",
    "planner.py",
    "classify_task.py",
    "feature_request_runner.py",
    "run_epic_task.py",
]


def main():
    for file_name in LEGACY_CANDIDATES:
        path = Path(file_name)
        status = "present" if path.exists() else "missing"
        print(f"{file_name}: {status}")


if __name__ == "__main__":
    main()
