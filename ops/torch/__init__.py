import torch
from graph import Graph
from graph.torch import ComputationNode
from .patch import TensorPatcher
import inspect


def computation_graph(model: torch.nn.Module, example_input: torch.Tensor) -> Graph:
    def hook_dataflow(hijacker, inputs, outputs):
        if not outputs:
            return

        print(hijacker.target_method_name)
        name = hijacker.target_method_name
        if inspect.isclass(hijacker.target_object) and hijacker.target_method_name in ['forward']:
            name = hijacker.target_object.__name__ + '.' + hijacker.target_method_name

        node = ComputationNode(name)
        for input in inputs:
            if not hasattr(input, '__producer_node'):
                input.__producer_node = ComputationNode()
            
            node.add_child(input.__producer_node)
        
        for output in outputs:
            output.__producer_node = node

    model.eval()
    example_input.__producer_node = ComputationNode('root')
    with torch.no_grad():
        with TensorPatcher(hook_dataflow):
            output = model(example_input)
            leaf = output.__producer_node
    
    return Graph(leaf)
