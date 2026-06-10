import subprocess

from orchestrator.product_registry import load_product_config
from orchestrator.repository_scanner import scan_repo
from orchestrator.affected_file_detector import detect_affected_files
from orchestrator.context_builder import read_context
from orchestrator.run_manager import make_run_dir, write_run_files
from orchestrator.prompt_builder import build_feature_prompt
from orchestrator.planner_agent import create_plan
from orchestrator.architect_agent import create_architecture_review
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.import_analyzer import analyze_imports, format_import_map


def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    return result.stdout.strip()



def main():
    product_name = input("Product name: ").strip()
    feature = input("Feature request: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    print(f"\nUsing repo: {repo_path}")

    print("\n[1] Scanning repository...")
    files = scan_repo(repo_path)

    print("\n[2] Building repository map...")
    repo_map = build_repository_map(files)
    repo_map_text = format_repository_map(repo_map)
    import_map = analyze_imports(repo_path, files)
    import_map_text = format_import_map(import_map)

    print("\n[3] Detecting affected files...")
    affected = detect_affected_files(feature, files)

    print("\nAffected files:")
    for file in affected:
        print(f"- {file}")

    print("\n[4] Building context...")
    context = read_context(repo_path, affected)

    print("\n[5] Creating implementation plan...")
    plan = create_plan(feature, affected)
    architecture_review = create_architecture_review(feature, affected, repo_map_text)

    print("\n[6] Creating run artifacts...")
    status = git_status(repo_path)
    prompt = build_feature_prompt(feature, repo_path, affected, context + '\n\n# Import Map\n\n' + import_map_text)

    run_dir = make_run_dir("feature")
    write_run_files(run_dir, feature, repo_path, files, affected, status, prompt)
    (run_dir / "plan.md").write_text(plan)
    (run_dir / "architecture-review.md").write_text(architecture_review)
    (run_dir / "repository-map.md").write_text(repo_map_text)
    (run_dir / "import-map.md").write_text(import_map_text)

    print(f"\nRun created: {run_dir}")
    print(f"Claude prompt: {run_dir / 'claude-prompt.md'}")


if __name__ == "__main__":
    main()
