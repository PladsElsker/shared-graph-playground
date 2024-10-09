import torch
from dataclasses import dataclass
from typing import Optional

from . import Node


@dataclass
class ComputationNode(Node):
    operation: Optional[str] = None
    meta: Optional[object] = None

    def __init__(self):
        super().__init__()

    def __hash__(self) -> str:
        return hash(self.uuid)

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return self.uuid
