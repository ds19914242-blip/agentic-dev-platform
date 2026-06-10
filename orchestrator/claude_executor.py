import subprocess
from pathlib import Path


def run_claude(repo_path, prompt):
    result = subprocess.run(
        ["claude", "--print", "--max-turns", "5", prompt],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Claude failed with code {result.returncode}\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
        )

    return result.stdout


def run_claude_from_file(repo_path, prompt_path):
    prompt = Path(prompt_path).read_text()

    max_chars = 50000
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "\n\n[TRUNCATED BY AGENTIC DEV PLATFORM]\n"

    return run_claude(repo_path, prompt)
