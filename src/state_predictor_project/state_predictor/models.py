import torch
import torch.nn as nn

class ResidualMLP(nn.Module):
    """
    Rede residual pequena.
    Entrada (por padrão): [x0, y0, sin0, cos0, x1, y1, sin1, cos1, dt] -> 9 dims
    Saída: delta em [dx, dy, d_sin, d_cos] -> 4 dims
    """
    def __init__(self, in_dim: int = 9, hidden: int = 64, out_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)
