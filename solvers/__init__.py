from graph import Graph, Node


class SharedGraphSolver:
    """
    Base class for implementing shared graph solvers. 
    Both graph1 and graph2 have been derived from a single original graph through the node-split operation. 
    You must find back the original graph connections. 
    """
    def solve(self, graph1: Graph, graph2: Graph) -> Graph:
        raise NotImplementedError()
