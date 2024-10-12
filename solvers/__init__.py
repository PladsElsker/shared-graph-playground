from graph import Graph, NodeMapping


class SharedGraphSolver:
    """
    Base class for implementing solvers. 
    """
    def solve(self, graph1: Graph, graph2: Graph) -> set[NodeMapping]:
        raise NotImplementedError()
