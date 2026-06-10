DOMAIN_HINTS = {
    "domain": ["criteria", "workflow", "analyze", "prefilter", "source", "feed"],
    "filter": ["criteria", "workflow", "prefilter", "analyze"],
    "rss": ["rss", "feed", "source", "collect"],
    "preview": ["preview", "uploadPreview", "PreviewPanel"],
    "export": ["export", "report", "pdf", "docx", "json", "markdown"],
    "auth": ["auth", "login", "session"],
    "dashboard": ["dashboard", "overview", "stats"],
    "summary": ["summary", "agent", "llm", "analysis"],
}


def score_file(feature, file):
    feature_l = feature.lower()
    file_l = file.lower()
    score = 0

    for word, hints in DOMAIN_HINTS.items():
        if word in feature_l:
            for hint in hints:
                if hint.lower() in file_l:
                    score += 3

    for token in feature_l.replace("-", " ").replace("_", " ").split():
        if len(token) >= 4 and token in file_l:
            score += 1

    if file.startswith("app/api/"):
        score += 1

    if file.startswith("src/"):
        score += 1

    if file.startswith("components/"):
        score += 0

    return score


def rank_affected_files(feature, files, limit=12):
    scored = []

    for file in files:
        score = score_file(feature, file)
        if score > 0:
            scored.append((score, file))

    scored.sort(key=lambda item: (-item[0], item[1]))

    return [file for _, file in scored[:limit]]
