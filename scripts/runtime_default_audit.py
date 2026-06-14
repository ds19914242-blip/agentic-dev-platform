from pathlib import Path
import subprocess


COMMANDS = [
    ["python3", "agentic.py", "help"],
    ["python3", "agentic.py", "agents"],
    [
        "python3",
        "agentic.py",
        "feature",
        "Audit runtime default path for Sources UI",
        "--product",
        "rss-agent-lab_2",
        "--output-dir",
        "runs/v15-runtime-default-audit",
    ],
]


def main():
    for command in COMMANDS:
        print("$ " + " ".join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            raise SystemExit(result.returncode)

    report = Path("runs/v15-runtime-default-audit/agent-report.md")
    if not report.exists():
        raise SystemExit("agent-report.md missing")

    print("runtime default audit passed")


if __name__ == "__main__":
    main()
