AGENTS = {
    "work_item_analyst": "Classifies incoming work and decides whether it should be decomposed first.",
    "planner": "Creates implementation plan and selects relevant files.",
    "architect": "Reviews architecture impact and risk.",
    "qa": "Creates QA and verification plan.",
    "implementer": "Executes approved implementation plan.",
    "validator": "Runs product validators and handles replan attempts.",
    "reviewer": "Reviews implementation output.",
    "acceptance": "Runs acceptance verification and creates recovery work on failure.",
    "release": "Finalizes run state and PR readiness.",
}


def agent_names():
    return sorted(AGENTS)


def describe_agent(name):
    return AGENTS.get(name, "")
