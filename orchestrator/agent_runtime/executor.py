from concurrent.futures import ThreadPoolExecutor, as_completed

from orchestrator.agent_runtime.observability.events import write_runtime_event


class AgentGraphExecutor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers

    def _emit(self, context, agent, status, message=""):
        write_runtime_event(
            context.run_dir,
            {
                "agent": agent,
                "status": status,
                "message": message,
            },
        )

    def _run_agent(self, node, context):
        self._emit(context, node.node_id, "started")
        try:
            result = node.agent.run(context)
            self._emit(
                context,
                node.node_id,
                "completed",
                f"status={result.status} confidence={result.confidence}",
            )
            return result
        except Exception as exc:
            self._emit(context, node.node_id, "failed", str(exc))
            raise

    def _maybe_recover_validation(self, graph, context, validation_result):
        if validation_result.status != "failed":
            return

        if not context.inputs.get("recovery_enabled"):
            return

        attempts = int(context.inputs.get("_validation_recovery_attempts", 0))
        max_attempts = int(context.inputs.get("max_recovery_attempts", 1))

        if attempts >= max_attempts:
            self._emit(context, "recovery", "skipped", "max attempts reached")
            return

        implementation = graph.nodes.get("implementation")
        validation = graph.nodes.get("validation")

        if not implementation or not validation:
            self._emit(context, "recovery", "skipped", "implementation or validation node missing")
            return

        context.inputs["_validation_recovery_attempts"] = attempts + 1
        self._emit(context, "recovery", "started", f"attempt={attempts + 1}")

        implementation_result = self._run_agent(implementation, context)
        graph.results["implementation"] = implementation_result
        context.inputs.setdefault("agent_results", graph.results)

        validation_result = self._run_agent(validation, context)
        graph.results["validation"] = validation_result
        context.inputs.setdefault("agent_results", graph.results)

        self._emit(context, "recovery", "completed", f"validation={validation_result.status}")

    def run(self, graph, context):
        while len(graph.results) < len(graph.nodes):
            ready = graph.ready_nodes()

            if not ready:
                raise RuntimeError("Agent graph has no ready nodes; dependency cycle or missing dependency")

            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                future_to_node = {
                    pool.submit(self._run_agent, node, context): node
                    for node in ready
                }

                for future in as_completed(future_to_node):
                    node = future_to_node[future]
                    result = future.result()
                    graph.results[node.node_id] = result
                    context.inputs.setdefault("agent_results", graph.results)

                    if node.node_id == "validation":
                        self._maybe_recover_validation(graph, context, result)

        return graph.results
