def build_repository_map(files):
    repo_map = {
        "api_routes": [],
        "pages": [],
        "components": [],
        "llm": [],
        "agents": [],
        "storage": [],
        "rss": [],
        "config": [],
        "tests": [],
        "other": [],
    }

    for file in files:
        if file.startswith("app/api/"):
            repo_map["api_routes"].append(file)
        elif file.startswith("app/") and file.endswith("page.tsx"):
            repo_map["pages"].append(file)
        elif file.startswith("components/"):
            repo_map["components"].append(file)
        elif file.startswith("src/llm/"):
            repo_map["llm"].append(file)
        elif file.startswith("src/agents/"):
            repo_map["agents"].append(file)
        elif file.startswith("lib/storage/"):
            repo_map["storage"].append(file)
        elif "rss" in file.lower() or "feed" in file.lower():
            repo_map["rss"].append(file)
        elif "config" in file.lower():
            repo_map["config"].append(file)
        elif "test" in file.lower() or "spec" in file.lower():
            repo_map["tests"].append(file)
        else:
            repo_map["other"].append(file)

    return repo_map


def format_repository_map(repo_map):
    lines = ["# Repository Map", ""]

    for section, items in repo_map.items():
        lines.append(f"## {section}")
        lines.append("")

        if items:
            for item in items[:50]:
                lines.append(f"- {item}")
        else:
            lines.append("_None detected_")

        lines.append("")

    return "\n".join(lines)
