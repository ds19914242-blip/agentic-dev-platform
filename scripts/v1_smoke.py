import subprocess


COMMANDS = [
    ["python3", "agentic.py", "help"],
    ["python3", "agentic.py", "agents"],
    [
        "python3",
        "agentic.py",
        "runtime-orchestrator",
        "UI change on Sources page",
        "--product",
        "rss-agent-lab_2",
        "--output-dir",
        "runs/v1-runtime-smoke",
    ],
    [
        "python3",
        "agentic.py",
        "dynamic-agent-graph",
        "UI change on Sources page",
        "--product",
        "rss-agent-lab_2",
        "--dry-run",
        "--output-dir",
        "runs/v1-dynamic-smoke",
    ],
]


def main():
    for command in COMMANDS:
        print("$ " + " ".join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            raise SystemExit(result.returncode)

    print("v1 smoke passed")


if __name__ == "__main__":
    main()
