from pathlib import Path

from orchestrator.approved_plan import save_approved_plan
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    run_dir = latest_run()
    response_path = run_dir / "claude-response.md"

    if response_path.exists():
        plan_text = response_path.read_text()
    else:
        plan_path = run_dir / "plan.md"
        plan_text = plan_path.read_text()

    save_approved_plan(run_dir, plan_text)
    write_status(run_dir, "plan_approved")
    append_event(run_dir, "Plan approved")

    print(f"Approved plan saved to: {run_dir / 'approved-plan.md'}")


if __name__ == "__main__":
    main()
