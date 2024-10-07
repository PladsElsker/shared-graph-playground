from graph import Graph
from ops import generate_subgraph

from node_editor import graph


def main():
    subgraph1: Graph = generate_subgraph(graph)
    subgraph2: Graph = generate_subgraph(graph)
    subgraph1 == subgraph2


if __name__ == '__main__':
    main()
