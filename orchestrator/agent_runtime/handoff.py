class AgentHandoff:
    def __init__(self):
        self.data = {}

    def write(self, agent_name, payload):
        self.data[agent_name] = payload

    def read(self, agent_name):
        return self.data.get(agent_name)
