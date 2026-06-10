from pathlib import Path

from orchestrator.confidence_gate import write_confidence_report
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    run_dir = latest_run()

    path, result = write_confidence_report(run_dir)

    if result["status"] == "passed":
        write_status(run_dir, "confidence_passed")
    elif result["status"] == "failed":
        write_status(run_dir, "confidence_failed")
    else:
        write_status(run_dir, "needs_review")

    append_event(run_dir, f"Confidence gate: {result['status']}")

    print(f"Confidence report saved to: {path}")
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")


if __name__ == "__main__":
    main()
