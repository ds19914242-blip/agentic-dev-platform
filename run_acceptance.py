import argparse
from pathlib import Path
from orchestrator.acceptance.runner import run_acceptance

def latest_epic_dir():
    backlog = Path("backlog")
    epics = sorted([p for p in backlog.glob("*") if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not epics:
        raise SystemExit("No backlog epic directories found.")
    return epics[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epic_dir", nargs="?")
    parser.add_argument("--command", default=None)
    parser.add_argument("--cwd", default=None)
    args = parser.parse_args()
    epic_dir = Path(args.epic_dir) if args.epic_dir else latest_epic_dir()
    result = run_acceptance(epic_dir=epic_dir, command=args.command, cwd=args.cwd)
    print(f"Epic: {epic_dir}")
    print(f"Command: {result.command}")
    print(f"Status: {passed if result.passed else failed}")
    print(f"Result: {epic_dir / acceptance-result.md}")
    if not result.passed:
        raise SystemExit(result.returncode or 1)

if __name__ == "__main__":
    main()
