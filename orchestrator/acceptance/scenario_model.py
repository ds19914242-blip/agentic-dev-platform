from dataclasses import dataclass, asdict


@dataclass
class AcceptanceScenario:
    title: str
    body: str
    steps: list
    expected: list

    def to_dict(self):
        return asdict(self)
