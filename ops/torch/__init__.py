import torch
from graph import Graph
from graph.torch import ComputationNode


def computation_graph(output_tensor: torch.Tensor) -> Graph:
    leaf = ComputationNode('leaf')
    last_root = None
    visited = {output_tensor.grad_fn: leaf}
    stack = [(output_tensor.grad_fn, leaf)]

    while stack:
        fn, node = stack.pop()

        for parent_fn, _ in fn.next_functions:
            if parent_fn is None:
                continue

            if parent_fn in visited:
                visited[parent_fn].add_child(node)
                last_root = visited[parent_fn]
            else:
                parent = ComputationNode(parent_fn.name())
                last_root = parent
                visited[fn] = node
                parent.add_child(node)
                stack.append((parent_fn, parent))

    root = ComputationNode('root')
    root.add_child(last_root)
    return Graph(root=root)
