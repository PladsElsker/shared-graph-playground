import random
import copy

from graph import Graph, Node


def subgraph(graph: Graph, max_splits: int = 4) -> Graph:
    """
    Split each node of the graph in up to `max_splits` nodes per node, and return the resulting graph. 
    """
    graph: Graph = copy.deepcopy(graph)
    graph.unique_indexes()

    visited: set[Node] = set([graph.root])
    stack: list[Node] = list(graph.root.children)
    while stack:
        node: Node = stack.pop()
        if node in visited:
            continue
        
        stack.extend(node.children)
        visited.add(node)
        
        splits: list[Node] = split_node(node, max_splits)
        for split in splits:
            visited.add(split)
    
    return graph


def split_node(node: Node, max_splits, allow_interconnectivity=False) -> list:
    """
    Split a node in up to `max_splits` nodes, and return the splits. 
    This operation mutates the graph in place. 
    """
    split_size = int(random.random() * max_splits) + 1
    splits = [Node() for _ in range(split_size)]

    for i, split in enumerate(splits):
        if allow_interconnectivity:
            inter_children = random.sample(splits[:i] + splits[i+1:], random.randint(0, len(splits) - 1))
            for to_add in inter_children:
                split.add_child(to_add)
        
        for parent in node.parents:
            parent.add_child(split)
        
        for child in node.children:
            split.add_child(child)

    node.remove()
    return splits
