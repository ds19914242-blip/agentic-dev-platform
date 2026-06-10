class AgentContext:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def to_markdown(self):
        lines = ["# Agent Context", ""]

        for key in sorted(self.data.keys()):
            lines.append(f"## {key}")
            lines.append("")
            lines.append(str(self.data[key])[:4000])
            lines.append("")

        return "\n".join(lines)
