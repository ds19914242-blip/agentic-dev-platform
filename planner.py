# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

PROMPT_FILE = "runs/latest-feature-prompt.md"

KEYWORDS = {
    "rss": ["app/rss", "app/api/rss", "lib/rss", "src/collector", "src/config/feeds"],
    "summary": ["components/SummaryCards", "components/ExecutiveSummary", "src/reporting", "src/report"],
    "ai": ["src/llm", "src/agents", "src/analysis"],
    "feed": ["lib/rss", "src/collector", "src/config/feeds"],
}


def extract_relevant_files(content):
    lines = content.splitlines()
    feature = ""
    files = []

    for i, line in enumerate(lines):
        if line.strip() == "# Feature Request" and i + 2 < len(lines):
            feature = lines[i + 2].lower()

        if line.endswith(".ts") or line.endswith(".tsx") or line.endswith(".json"):
            files.append(line.strip())

    matched = []

    for word, patterns in KEYWORDS.items():
        if word in feature:
            for file in files:
                if any(file.startswith(pattern) for pattern in patterns):
                    matched.append(file)

    return sorted(set(matched))


def main():
    content = Path(PROMPT_FILE).read_text()
    affected_files = extract_relevant_files(content)

    print("\n=== AFFECTED FILES ===\n")

    if not affected_files:
        print("No affected files detected.")
    else:
        for file in affected_files:
            print(f"- {file}")

    print("\n=== IMPLEMENTATION PLAN ===\n")
    print("1. Read affected files")
    print("2. Identify where RSS items are collected and analyzed")
    print("3. Identify where summaries are generated or displayed")
    print("4. Implement feature in the smallest safe scope")
    print("5. Run tests or typecheck")
    print("6. Review git diff")


if __name__ == "__main__":
    main()
