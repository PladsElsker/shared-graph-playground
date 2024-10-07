import random
import copy

from graph import Graph, Node


def exclusive_subgraphs(graph: Graph, max_splits: int = 10) -> list:
    """
    Split each node of the graph in up to `max_splits` nodes per node, and return the resulting derived graphs A and B.
    Node splitting is exclusive between the nodes of the derived graphs A and B. 
    This means that each splitted node can only be applied to 1 node between graph A and B, and the other will stay untouched. 
    """
    graph_a: Graph = copy.deepcopy(graph)
    graph_b: Graph = copy.deepcopy(graph)
    
    original_nodes = graph.get_nodes()
    nodes_a = graph_a.get_nodes()
    nodes_b = graph_b.get_nodes()

    for i, _ in enumerate(original_nodes):
        if random.randint(0, 1) % 2 == 0:
            split_node(nodes_a[i], max_splits)
        else:
            split_node(nodes_b[i], max_splits)
    
    graph_a.unique_indexes()
    graph_b.unique_indexes()
    return graph_a, graph_b


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
