import torch
import torch.nn as nn

class ResidualMLP(nn.Module):
    """
    Rede residual ego-cêntrica.
    Entrada: [dt, v_med, w_med, v_std, w_std] -> 5 dims
    Saída: delta em [dx_local, dy_local, dth_local] -> 3 dims
    """
    def __init__(self, in_dim: int = 5, hidden: int = 64, out_dim: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.BatchNorm1d(in_dim),
            nn.Linear(in_dim, hidden),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.1),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        if x.dim() == 1:
            x = x.unsqueeze(0)
            return self.net(x).squeeze(0)
        return self.net(x)
