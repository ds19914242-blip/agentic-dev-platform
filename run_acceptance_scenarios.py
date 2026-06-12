import argparse
from pathlib import Path

from orchestrator.acceptance.scenario_parser import write_scenarios_json
from orchestrator.acceptance.scenario_report import write_scenario_report
from orchestrator.acceptance.playwright_generator import generate_playwright_test


def latest_epic_dir():
    backlog = Path("backlog")
    epics = sorted([p for p in backlog.glob("*") if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not epics:
        raise SystemExit("No backlog epic directories found.")
    return epics[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epic_dir", nargs="?")
    args = parser.parse_args()
    epic_dir = Path(args.epic_dir) if args.epic_dir else latest_epic_dir()
    output_path, scenarios = write_scenarios_json(epic_dir)
    report_path = write_scenario_report(epic_dir, scenarios)
    playwright_path = generate_playwright_test(epic_dir, scenarios)
    print(f"Epic: {epic_dir}")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")
    print(f"Playwright: {playwright_path}")


if __name__ == "__main__":
    main()
