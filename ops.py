import random
import copy

from graph import Graph, Node


def generate_subgraph(graph: Graph, max_splits: int = 1) -> Graph:
    """
    Split each node of the graph in up to `max_splits` nodes per node, and return the resulting graph. 
    """
    graph: Graph = copy.deepcopy(graph)

    root_splits: list[Node] = split_node(graph.root, max_splits)
    new_root: Node = Node()
    visited: set[Node] = set([new_root])
    for root_split in root_splits:
        new_root.add_child(root_split)
        visited.add(root_split)

    graph: Graph = Graph(root=new_root)

    stack: list[Node] = list(set(n for split in root_splits for n in split.children))
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

    node.remove()

    for i, split in enumerate(splits):
        if allow_interconnectivity:
            inter_children = random.sample(splits[:i] + splits[i+1:], random.randint(0, len(splits) - 1))
            for to_add in inter_children:
                split.add_child(to_add)
        
        for parent in node.parents:
            parent.add_child(split)
        
        for child in node.children:
            split.add_child(child)

    return splits
