import subprocess
from pathlib import Path


def run_claude(repo_path, prompt, allow_writes=False, max_turns=15):
    command = ["claude", "--print", "--max-turns", str(max_turns)]

    if allow_writes:
        command.append("--dangerously-skip-permissions")

    command.append(prompt)

    result = subprocess.run(
        command,
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Claude failed with code {result.returncode}\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
        )

    return result.stdout


def run_claude_from_file(repo_path, prompt_path, allow_writes=False):
    prompt = Path(prompt_path).read_text()

    max_chars = 50000
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "\n\n[TRUNCATED BY AGENTIC DEV PLATFORM]\n"

    return run_claude(repo_path, prompt, allow_writes=allow_writes)
