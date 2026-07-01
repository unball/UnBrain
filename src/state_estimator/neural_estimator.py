import torch
import torch.nn as nn

class NeuralStateEstimator(nn.Module):
    """
    Arquitetura de Estimação de Estado baseada em Recorrência (NARX).
    Responsabilidade: Aprender a função de resíduo (Dynamics Gap) que a 
    física analítica falha em prever (atrito, folga mecânica, atraso da câmera).
    """
    def __init__(self, history_size: int = 10, hidden_dim: int = 64):
        super(NeuralStateEstimator, self).__init__()
        self.history_size = history_size
        self.input_features = 9
        self.output_dim = 6
        self.hidden_dim = hidden_dim
        
        # Constantes de Normalização Padrão. 
        # (Escalonam os dados para evitar explosão de gradiente na GRU).
        self.register_buffer(
            "norm_scale", 
            torch.tensor([0.875, 0.675, 1.0, 1.0, 1.5, 10.0, 0.024, 0.024, 0.16], dtype=torch.float32)
        )
        self.register_buffer(
            "output_scale", 
            torch.tensor([0.875, 0.675, 1.0, 2.0, 2.0, 10.0], dtype=torch.float32)
        )

        # Core Temporal
        self.gru = nn.GRU(
            input_size=self.input_features,
            hidden_size=self.hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )
        
        # Cabeçalho Multi-Layer Perceptron (Decodificador de Estado)
        self.fc = nn.Sequential(
            nn.Linear(self.hidden_dim, 64),
            nn.Mish(), # Mish é analiticamente mais contínua e gera gradientes melhores que ReLU em robótica
            nn.Linear(64, self.output_dim)
        )

    def forward(self, history: torch.Tensor) -> torch.Tensor:
        """
        Grafo computacional compatível com TorchScript estrito.
        """
        # Normalização física
        history_norm = history / self.norm_scale
        
        # Garantia de dimensionalidade [Batch, SeqLen, Features]
        if history_norm.dim() == 2:
            history_norm = history_norm.unsqueeze(0)
            is_2d = True
        else:
            is_2d = False
            
        # Extração temporal
        # Retorno: out = [Batch, SeqLen, HiddenDim]
        out, _ = self.gru(history_norm)
        
        # Extrai estado oculto do t mais recente
        last_out = out[:, -1, :]
        
        # Predição de resíduo
        pred_norm = self.fc(last_out)
        
        # Restaura dimensão e escala física real (Metros / Radianos)
        if is_2d:
            pred_norm = pred_norm.squeeze(0)
            
        return pred_norm * self.output_scale

    @torch.jit.export
    def get_scales(self) -> torch.Tensor:
        """ Método de utilidade para quem precisar das escalas no PPO """
        return self.output_scale