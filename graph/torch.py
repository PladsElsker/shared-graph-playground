import json
from dataclasses import dataclass
from typing import Optional

from . import Node


@dataclass
class ComputationNode(Node):
    operation: Optional[str] = None

    def __init__(self, operation=None):
        super().__init__()
        self.operation = operation

    def __hash__(self) -> str:
        return hash(self.uuid)

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return self.uuid
    
    def serialize(self) -> str:
        return json.dumps({
            'uuid': self.uuid,
            'children': [n.uuid for n in self.children],
            'parents': [n.uuid for n in self.parents],
            'operation': self.operation,
        })
