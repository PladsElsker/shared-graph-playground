from graph import Graph
from ops import subgraph

from node_editor import graph
from solvers.example import ExampleSolver


def main():
    subgraph1: Graph = subgraph(graph)
    subgraph2: Graph = subgraph(graph)

    print(graph == ExampleSolver().solve(subgraph1, subgraph2))


if __name__ == '__main__':
    main()
