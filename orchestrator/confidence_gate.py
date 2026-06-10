from pathlib import Path


def read_validation_result(run_dir):
    path = Path(run_dir) / "validation.md"

    if not path.exists():
        return "missing"

    text = path.read_text().lower()

    if "failed" in text and "overall result" in text:
        return "failed"

    if "passed" in text and "overall result" in text:
        return "passed"

    if "failed" in text:
        return "failed"

    if "passed" in text:
        return "passed"

    return "unknown"


def read_post_run_review(run_dir):
    path = Path(run_dir) / "post-run-review.md"

    if not path.exists():
        return {
            "unexpected": [],
            "missing": [],
        }

    text = path.read_text().splitlines()

    current = None
    unexpected = []
    missing = []

    for line in text:
        line = line.strip()

        if line == "## Unexpected Changes":
            current = "unexpected"
            continue

        if line == "## Expected But Not Changed":
            current = "missing"
            continue

        if line.startswith("## "):
            current = None
            continue

        if line.startswith("- "):
            if current == "unexpected":
                unexpected.append(line[2:])
            elif current == "missing":
                missing.append(line[2:])

    return {
        "unexpected": unexpected,
        "missing": missing,
    }


def evaluate_confidence(run_dir):
    validation = read_validation_result(run_dir)
    review = read_post_run_review(run_dir)

    unexpected = review["unexpected"]
    missing = review["missing"]

    if validation == "failed":
        status = "failed"
        reason = "Validation failed."
    elif validation in {"missing", "unknown"}:
        status = "needs_review"
        reason = "Validation result is missing or unknown."
    elif len(unexpected) >= 5:
        status = "needs_review"
        reason = "Too many unexpected changed files."
    else:
        status = "passed"
        if missing:
            reason = "Validation passed. Some expected files were not changed, but this is treated as a non-blocking warning."
        else:
            reason = "Validation passed and file changes look acceptable."

    return {
        "status": status,
        "reason": reason,
        "validation": validation,
        "unexpected": unexpected,
        "missing": missing,
    }


def write_confidence_report(run_dir):
    result = evaluate_confidence(run_dir)

    path = Path(run_dir) / "confidence.md"

    path.write_text(f"""# Confidence Gate

## Status

{result["status"]}

## Reason

{result["reason"]}

## Validation

{result["validation"]}

## Unexpected Changes

{chr(10).join("- " + f for f in result["unexpected"]) or "_None_"}

## Expected But Not Changed

{chr(10).join("- " + f for f in result["missing"]) or "_None_"}
""")

    return path, result
