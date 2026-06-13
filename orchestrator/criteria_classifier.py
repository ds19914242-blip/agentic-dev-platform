def classify_criterion(description):
    text = description.lower()

    if any(word in text for word in [
        "route", "page", "страница", "переход", "/",
    ]):
        return "route"

    if any(word in text for word in [
        "build", "typecheck", "validator", "npm run", "passes", "проходит",
    ]):
        return "validator"

    if any(word in text for word in [
        "visible", "видим", "отображ", "footer", "ui", "интерфейс",
        "button", "toggle", "карточ", "экран",
    ]):
        return "ui"

    return "manual"


def evidence_sources_for_type(criterion_type):
    if criterion_type == "route":
        return ["route-verification.md"]

    if criterion_type == "validator":
        return ["validation.md", "validation.json"]

    if criterion_type == "ui":
        return ["verification-evidence.md"]

    return ["verification-evidence.md"]
