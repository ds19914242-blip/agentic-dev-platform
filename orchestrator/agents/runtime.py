from orchestrator.agents.context import AgentRunContext
from orchestrator.agents.registry import describe_agent
from orchestrator.agents.definition_loader import load_agent_definition
from orchestrator.agents.result import passed, failed, write_agent_result


def run_agent(agent_name, context):
    if not isinstance(context, AgentRunContext):
        raise TypeError("context must be AgentRunContext")

    description = describe_agent(agent_name)
    definition = load_agent_definition(agent_name)

    if not description and not definition:
        result = failed(
            agent_name,
            f"Unknown agent: {agent_name}",
            next_actions=["Register this agent before execution."],
        )
    else:
        result = passed(
            agent_name,
            f"Agent '{agent_name}' contract loaded. Runtime execution is available.",
            metadata={
                "description": description,
                "definition": definition or {},
                "product_name": context.product_name,
                "repo_path": context.repo_path,
                "feature": context.feature,
                "task_path": context.task_path,
                "inputs": context.inputs,
            },
        )

    if context.run_dir:
        write_agent_result(context.run_dir, result)

    return result
