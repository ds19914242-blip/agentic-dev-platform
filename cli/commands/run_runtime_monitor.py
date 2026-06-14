import argparse
import time

from orchestrator.agent_runtime.observability.events import read_runtime_events


def print_events(run_dir):
    events = read_runtime_events(run_dir)

    if not events:
        print("No runtime events yet.")
        return

    for event in events:
        print(
            f"{event.get('time')} "
            f"{event.get('agent', '-'):24} "
            f"{event.get('status', '-'):12} "
            f"{event.get('message', '')}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    if not args.follow:
        print_events(args.run_dir)
        return

    seen = 0

    while True:
        events = read_runtime_events(args.run_dir)
        for event in events[seen:]:
            print(
                f"{event.get('time')} "
                f"{event.get('agent', '-'):24} "
                f"{event.get('status', '-'):12} "
                f"{event.get('message', '')}",
                flush=True,
            )
        seen = len(events)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
