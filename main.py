import torch

from ops.torch import computation_graph
from models.spectral_ar_vit import ArSpectralDiffusionTransformer


def main():
    """"
    input_dim = 10
    hidden_dim = 16
    output_dim = 5
    input = torch.randn(5, input_dim)
    model = ThreeOperationModel(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)
    input = torch.randn(5, 4)
    model = SimpleModel()

    input = torch.rand(1, 32, 17, 4, requires_grad=True).to(torch.complex64)
    model = ArSpectralDiffusionTransformer(blocks=5)
    """
    input = torch.rand(1, 4, 512 // 8, 512 // 8, requires_grad=True, dtype=torch.float16, device='cuda')
    from models.sdxl import model

    graph = computation_graph(model(input))
    graph = graph.regular_2()

    json_data = graph.serialize()
    with open('graph/render/graphData.json', 'w') as graph_file:
        graph_file.write(json_data)


if __name__ == '__main__':
    main()
