import torch


class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(4, 3)
        self.fc2 = torch.nn.Linear(3, 2)

    def forward(self, x):
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.fc2(x)
        return x


class ThreeOperationModel(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(ThreeOperationModel, self).__init__()
        self.op1 = torch.nn.Linear(input_dim, hidden_dim)
        self.op2 = torch.nn.Linear(input_dim, hidden_dim)
        self.op3 = torch.nn.Conv1d(in_channels=1, out_channels=hidden_dim, kernel_size=3, padding=1)
        self.combination = torch.nn.Linear(hidden_dim * 3, output_dim)
    
    def forward(self, x):
        out1 = self.op1(x)
        out2 = torch.relu(self.op2(x))
        out3 = x.unsqueeze(1)
        out3 = self.op3(out3)
        out3 = out3.mean(dim=2)
        x = torch.cat((out1, out2, out3), dim=-1)
        x = self.combination(x)
        return x
