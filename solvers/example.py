from graph import Graph, Node
from . import SharedGraphSolver


class ExampleSolver(SharedGraphSolver):
    def solve(self, graph1: Graph, graph2: Graph) -> Graph:
        return graph1
