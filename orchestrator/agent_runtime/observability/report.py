from pathlib import Path

from orchestrator.agent_runtime.observability.events import read_runtime_events


def write_runtime_timeline(run_dir):
    run_dir = Path(run_dir)
    events = read_runtime_events(run_dir)

    lines = ["# Runtime Timeline", ""]

    if not events:
        lines.append("_No runtime events captured._")
    else:
        for event in events:
            agent = event.get("agent", "-")
            status = event.get("status", "-")
            message = event.get("message", "")
            lines.append(f"- {event.get('time')} `{agent}` {status} {message}".rstrip())

    path = run_dir / "runtime-timeline.md"
    path.write_text("\n".join(lines) + "\n")

    return path
