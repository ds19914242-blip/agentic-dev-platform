from concurrent.futures import ThreadPoolExecutor, as_completed


class AgentGraphExecutor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers

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
                    graph.results[node.node_id] = future.result()

        return graph.results
