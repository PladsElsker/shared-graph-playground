from graph import Graph, Node


def shortest_index_map(leaf: Node):
    index_map = {leaf: 0}
    stack = [leaf]
    while stack:
        node = stack.pop()
        index = index_map[node]

        for parent in node.parents:
            if parent in index_map:
                continue

            index_map[parent] = index + 1
            stack.append(parent)
    