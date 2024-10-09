import torch
from torch.fx.passes.shape_prop import ShapeProp

from graph import Graph
from graph.torch import ComputationNode


def computation_graph(model: torch.nn.Module, example_input: torch.Tensor) -> Graph:
    """
    Extract the computation graph of a torch model along with some additional data for each node. 

    """
    tracer = torch.fx.symbolic_trace(model)
    graph_module = tracer.graph
    ShapeProp(tracer).propagate(example_input)
    node_map = {}

    fx_root = next((_ for _ in reversed(graph_module.nodes)))
    root = resolve_graph_connections(fx_root, node_map)
    return Graph(root).reverse_connections()


def resolve_graph_connections(fx_node: torch.fx.node.Node, visited: dict = None) -> ComputationNode:
    """
    Recursively resolve connections between nodes, building the graph.
    """
    if visited is None:
        visited = {}

    if fx_node in visited:
        return visited[fx_node]
    
    node = convert_fx_node(fx_node)

    for arg in fx_node.all_input_nodes:
        if isinstance(arg, torch.fx.Node):
            child_node = resolve_graph_connections(arg, visited)
            node.add_child(child_node)
    
    visited[fx_node] = node
    return node


def convert_fx_node(fx_node: torch.fx.node.Node) -> ComputationNode:
    node = ComputationNode()
    node.operation = fx_node.op
    if 'tensor_meta' in fx_node.meta:
        node.meta = fx_node.meta['tensor_meta']

    return node
