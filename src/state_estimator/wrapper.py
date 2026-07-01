import torch
import math
from typing import Tuple, Optional

class RobustStateEstimator:
    """
    Estimador de Estados Neural Robusto (NARX + Unicycle Exact Integration).
    Criado pelo Engenheiro da UnBall para garantir máxima fidelidade física e
    extrema baixa latência. Agnóstico de controlador (PID, LQR ou PPO).
    """
    def __init__(self, history_size: int = 10, model_path: Optional[str] = None):
        self.history_size = history_size
        self.dt = 0.016  # Período de amostragem padrão (60Hz)
        
        # Buffer circular in-place pré-alocado O(1) allocs
        # Formato: [x, y, sin_th, cos_th, v, w, dx_kin, dy_kin, dtheta_kin]
        self.buffer = torch.zeros((history_size, 9), dtype=torch.float32)
        
        # Memória de estado para Dead Reckoning (Cegueira da câmera)
        self.last_estimated_x = 0.0
        self.last_estimated_y = 0.0
        self.last_estimated_th = 0.0
        
        # Últimos comandos atuados
        self.last_v = 0.0
        self.last_w = 0.0

        # Otimização drástica de CPU para a Thread do Controlador
        if torch is not None:
            torch.set_num_threads(1)
            # Para inferência extrema, desativamos gradientes globalmente na thread
            torch.set_grad_enabled(False) 

        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str]):
        """Inicializa ou carrega o modelo compilado via TorchScript (JIT)."""
        if model_path:
            try:
                self.model = torch.jit.load(model_path, map_location='cpu')
                self.model.eval()
                print(f"[RobustStateEstimator] Sucesso ao carregar: {model_path}")
            except Exception as e:
                print(f"[RobustStateEstimator] Falha crítica ao carregar modelo: {e}")
                self.model = None
        else:
            from .neural_estimator import NeuralStateEstimator
            self.model = torch.jit.script(NeuralStateEstimator(self.history_size))
            self.model.eval()

    def push_command(self, v: float, w: float) -> None:
        """
        Registra os comandos de velocidade linear e angular (Setpoints de controle).
        Esses valores são a raiz da nossa predição cinemática.
        """
        self.last_v = float(v)
        self.last_w = float(w)

    def _calculate_exact_kinematics(self, theta: float) -> Tuple[float, float, float]:
        """
        FÍSICA ROBUSTA: Integração exata do modelo Uniciclo.
        Diferente da integração de Euler (v * cos(th) * dt), esta equação não sofre
        phase-lag durante curvas em alta velocidade.
        """
        if abs(self.last_w) < 1e-4:
            # Regra de L'Hôpital para limites onde w tende a 0 (Reta perfeita)
            dx = self.last_v * math.cos(theta) * self.dt
            dy = self.last_v * math.sin(theta) * self.dt
            dth = self.last_w * self.dt
        else:
            # Integração circular exata (Arc trajectory)
            theta_next = theta + self.last_w * self.dt
            dx = (self.last_v / self.last_w) * (math.sin(theta_next) - math.sin(theta))
            dy = -(self.last_v / self.last_w) * (math.cos(theta_next) - math.cos(theta))
            dth = self.last_w * self.dt
            
        return dx, dy, dth

    def push_vision(self, x: float, y: float, theta: float) -> None:
        """
        Acopla medição da câmera com o vetor cinemático para criar o input da GRU.
        """
        # Deslizamento do buffer de memória usando in-place copy (Sem Garbage Collection)
        self.buffer.copy_(torch.roll(self.buffer, shifts=-1, dims=0))
        
        # Envelopamento matemático estrito de -pi a pi
        theta = (float(theta) + math.pi) % (2 * math.pi) - math.pi
        
        # Prior cinemático (Nosso palpite inicial baseado na física do robô)
        dx_kin, dy_kin, dtheta_kin = self._calculate_exact_kinematics(theta)
        
        # Escrita in-place no frame mais recente (índice -1)
        self.buffer[-1, 0] = float(x)
        self.buffer[-1, 1] = float(y)
        self.buffer[-1, 2] = math.sin(theta)
        self.buffer[-1, 3] = math.cos(theta)
        self.buffer[-1, 4] = self.last_v
        self.buffer[-1, 5] = self.last_w
        self.buffer[-1, 6] = dx_kin
        self.buffer[-1, 7] = dy_kin
        self.buffer[-1, 8] = dtheta_kin

    def predict(self) -> Tuple[float, float, float, float, float, float]:
        """
        Inferência da Rede Neural NARX.
        O modelo prediz o resíduo estocástico (Ruído, folga de engrenagem, atraso).
        """
        last_raw_x = float(self.buffer[-1, 0])
        last_raw_y = float(self.buffer[-1, 1])
        last_raw_th = math.atan2(float(self.buffer[-1, 2]), float(self.buffer[-1, 3]))

        if self.model is None:
            # Fallback passivo: Se a IA falhar, não derrube o robô. Retorna medição limpa.
            return last_raw_x, last_raw_y, last_raw_th, 0.0, 0.0, 0.0
            
        # Contexto de inferência extrema (Mais rápido e consome menos RAM que no_grad)
        with torch.inference_mode():
            # Passagem direta pelo grafo JIT
            pred_residual = self.model(self.buffer)
            
            x_res, y_res, th_res = float(pred_residual[0]), float(pred_residual[1]), float(pred_residual[2])
            
            # Watchdog Físico: Se o resíduo for absurdo (> 40cm), a IA divergiu ou a câmera teleportou.
            if math.hypot(x_res, y_res) > 0.4:
                return last_raw_x, last_raw_y, last_raw_th, 0.0, 0.0, 0.0
            
            # Fusão de Dados: Leitura Raw + Correção Neural
            self.last_estimated_x = last_raw_x + x_res
            self.last_estimated_y = last_raw_y + y_res
            self.last_estimated_th = (last_raw_th + th_res + math.pi) % (2 * math.pi) - math.pi
            
            # Velocidades inferidas latentes
            vx, vy, vw = float(pred_residual[3]), float(pred_residual[4]), float(pred_residual[5])
            
            return self.last_estimated_x, self.last_estimated_y, self.last_estimated_th, vx, vy, vw

    def predictOnly(self) -> Tuple[float, float, float, float, float, float]:
        """
        DEAD RECKONING PURO (Falha de Visão).
        Em vez de repetir a câmera velha (o que causaria phase-lag massivo),
        nós evoluímos o último estado estimado através do nosso modelo cinemático puro!
        """
        # Integra o quanto o robô deveria ter andado fisicamente desde o último frame
        dx_kin, dy_kin, dth_kin = self._calculate_exact_kinematics(self.last_estimated_th)
        
        dr_x = self.last_estimated_x + dx_kin
        dr_y = self.last_estimated_y + dy_kin
        dr_th = (self.last_estimated_th + dth_kin + math.pi) % (2 * math.pi) - math.pi
        
        # "Engana" a rede neural alimentando seu buffer com a nossa dedução física
        # Isso garante que a memória temporal da GRU não corrompa enquanto a visão não volta.
        self.push_vision(dr_x, dr_y, dr_th)
        
        return self.predict()