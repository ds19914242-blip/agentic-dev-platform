# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

from orchestrator.claude_response import save_claude_response
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    print("Paste Claude response below.")
    print("When finished, press Ctrl+D.")
    print()

    response = ""

    try:
        while True:
            response += input() + "\n"
    except EOFError:
        pass

    run_dir = latest_run()
    path = save_claude_response(run_dir, response)
    write_status(run_dir, "response_recorded")
    append_event(run_dir, "Claude response recorded")

    print(f"Saved Claude response to: {path}")


if __name__ == "__main__":
    main()
