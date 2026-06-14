import argparse

from orchestrator.repository_analyst import analyze_repository


def main():
    parser = argparse.ArgumentParser(description="Analyze a connected repository (step 0).")
    parser.add_argument("product", help="Product name (folder under products/)")
    parser.add_argument("--no-write", action="store_true", help="Print only, do not write to memory")
    args = parser.parse_args()

    result = analyze_repository(args.product, write=not args.no_write)

    print(f"Repository Analyst: {args.product}")
    print(f"Repo: {result['repo_path']}")
    print(f"Files scanned: {result['file_count']}")
    print(f"LLM analysis: {'yes' if result['agent_ran'] else 'no (fallback map only)'}")
    if result.get("analysis_path"):
        print(f"Written: {result['analysis_path']}")
        print("Memory updated: product-memory.codebase_summary, architecture-memory")
    print()
    if result["summary"]:
        print("Summary:")
        print(result["summary"])


if __name__ == "__main__":
    main()
