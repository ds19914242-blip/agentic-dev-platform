from orchestrator.agent_runtime.builtin_agents import create_builtin_registry


def main():
    registry = create_builtin_registry()

    for agent in registry.list():
        print(f"{agent.name}")
        print(f"  description: {agent.description}")
        print(f"  runtime: agent_runtime")
        print()


if __name__ == "__main__":
    main()
