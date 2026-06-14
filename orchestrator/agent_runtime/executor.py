from concurrent.futures import ThreadPoolExecutor, as_completed


class AgentGraphExecutor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers

    def _run_node(self, graph, node, context):
        result = node.agent.run(context)
        graph.results[node.node_id] = result
        context.inputs.setdefault("agent_results", graph.results)
        return result

    def _maybe_recover_validation(self, graph, context, validation_result):
        if validation_result.status != "failed":
            return

        if not context.inputs.get("recovery_enabled"):
            return

        attempts = int(context.inputs.get("_validation_recovery_attempts", 0))
        max_attempts = int(context.inputs.get("max_recovery_attempts", 1))

        if attempts >= max_attempts:
            return

        implementation = graph.nodes.get("implementation")
        validation = graph.nodes.get("validation")

        if not implementation or not validation:
            return

        context.inputs["_validation_recovery_attempts"] = attempts + 1

        implementation_result = implementation.agent.run(context)
        graph.results["implementation"] = implementation_result
        context.inputs.setdefault("agent_results", graph.results)

        validation_result = validation.agent.run(context)
        graph.results["validation"] = validation_result
        context.inputs.setdefault("agent_results", graph.results)

    def run(self, graph, context):
        while len(graph.results) < len(graph.nodes):
            ready = graph.ready_nodes()

            if not ready:
                raise RuntimeError("Agent graph has no ready nodes; dependency cycle or missing dependency")

            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                future_to_node = {
                    pool.submit(node.agent.run, context): node
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
