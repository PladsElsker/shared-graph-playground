from graph import Graph
from ops import exclusive_subgraphs

from node_editor import graph
from solvers.example import ExampleSolver


def main():
    subgraph1, subgraph2 = exclusive_subgraphs(graph)
    print(graph == ExampleSolver().solve(subgraph1, subgraph2))


if __name__ == '__main__':
    main()
