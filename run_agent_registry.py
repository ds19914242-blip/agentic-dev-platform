from orchestrator.agents.definition_loader import load_agent_definition
from orchestrator.agents.registry import agent_names, describe_agent


def main():
    for name in agent_names():
        definition = load_agent_definition(name)
        print(f"{name}")
        print(f"  description: {describe_agent(name)}")

        if definition:
            print(f"  mission: {definition.get('mission', '')}")
            print(f"  blocking: {definition.get('blocking', False)}")
            print(f"  definition: {definition.get('definition_path')}")
        else:
            print("  definition: missing")

        print()


if __name__ == "__main__":
    main()
