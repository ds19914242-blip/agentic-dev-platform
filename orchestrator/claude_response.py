from pathlib import Path


def save_claude_response(run_dir, response_text):
    path = Path(run_dir) / "claude-response.md"

    path.write_text(f"""# Claude Response

{response_text}
""")

    return path
