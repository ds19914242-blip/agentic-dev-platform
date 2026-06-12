from orchestrator.approved_plan import save_approved_plan
from orchestrator.claude_executor import run_claude_from_file
from orchestrator.claude_response import save_claude_response
from orchestrator.run_decision import decide_after_planning, decide_after_security, write_decision


def run_claude_planning_and_approve(
    repo_path,
    run_dir,
    run,
    graph,
    graph_v2,
):
    run.status("planning_with_claude")
    run.event("Claude planning started")

    claude_plan_response = run_claude_from_file(
        repo_path,
        run_dir / "claude-prompt.md",
        allow_writes=False,
    )

    save_claude_response(run_dir, claude_plan_response)
    run.artifact("claude-response.md", stage="claude_plan")
    graph.mark_completed("claude_plan")
    run.event("Claude planning response recorded")
    graph_v2.complete("claude_plan", artifacts=["claude-response.md"])
    graph_v2.write()

    planning_decision = decide_after_planning(run_dir)
    write_decision(run_dir, "planning", planning_decision)

    if planning_decision["decision"] == "stop":
        run.status(planning_decision["status"])
        run.event(f"Stopped after planning: {planning_decision['reason']}")
        print(f"Run stopped after planning: {planning_decision['status']}")
        return {
            "stopped": True,
            "claude_plan_response": claude_plan_response,
        }

    security_decision = decide_after_security(run_dir)
    write_decision(run_dir, "security", security_decision)
    run.event(f"Security decision advisory: {security_decision['status']}")

    save_approved_plan(run_dir, claude_plan_response)
    run.artifact("approved-plan.md", stage="approved_plan")
    graph.mark_completed("approved_plan")
    run.status("plan_approved")
    run.event("Plan automatically approved")
    graph_v2.complete("approved_plan", artifacts=["approved-plan.md"])
    graph_v2.write()

    return {
        "stopped": False,
        "claude_plan_response": claude_plan_response,
        "security_decision": security_decision,
    }
