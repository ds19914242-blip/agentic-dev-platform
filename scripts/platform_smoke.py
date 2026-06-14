import subprocess
import sys


COMMANDS = [
    ["python3", "agentic.py", "help"],
    ["python3", "agentic.py", "agents"],
    [
        "python3",
        "agentic.py",
        "dynamic-agent-graph",
        "UI change on Sources page",
        "--product",
        "rss-agent-lab_2",
        "--dry-run",
        "--output-dir",
        "runs/v039-dynamic-smoke",
    ],
    [
        "python3",
        "agentic.py",
        "multi-agent-graph",
        "Fan-out smoke",
        "--product",
        "rss-agent-lab_2",
        "--dry-run",
        "--output-dir",
        "runs/v039-multi-smoke",
    ],
]


def main():
    for command in COMMANDS:
        print("$ " + " ".join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            print(f"FAILED: {' '.join(command)}")
            raise SystemExit(result.returncode)

    print("Platform smoke passed")


if __name__ == "__main__":
    main()
