KEYWORDS = {
    "rss": ["app/rss", "app/api/rss", "lib/rss", "src/collector", "src/config/feeds"],
    "summary": ["components", "src/reporting", "src/report", "src/agents"],
    "summaries": ["components", "src/reporting", "src/report", "src/agents"],
    "ai": ["src/llm", "src/agents", "src/analysis"],
    "feed": ["lib/rss", "src/collector", "src/config/feeds"],
    "preview": ["components/PreviewPanel", "lib/uploadPreview", "app/api/rss/summarize"],
}


def detect_affected_files(feature, files):
    feature_l = feature.lower()
    matched = []

    for word, patterns in KEYWORDS.items():
        if word in feature_l:
            for file in files:
                if any(file.startswith(pattern) for pattern in patterns):
                    matched.append(file)

    return sorted(set(matched))[:15]
