from graph import Graph
from ops import generate_subgraph

from node_editor import graph as shared_graph
from solvers.example import ExampleSolver


def main():
    subgraph1: Graph = generate_subgraph(shared_graph)
    subgraph2: Graph = generate_subgraph(shared_graph)

    print(shared_graph == ExampleSolver().solve(subgraph1, subgraph2))


if __name__ == '__main__':
    main()
