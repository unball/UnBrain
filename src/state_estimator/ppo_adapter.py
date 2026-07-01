# ppo_adapter.py (Somente usado durante treino de IA)
import math
from state_estimator.wrapper import RobustStateEstimator

class RLStateAdapter:
    """ 
    Design Pattern Adapter: Formata dados do Estimador Físico
    exclusivamente para o formato padronizado (-1 a 1) do PPO.
    """
    def __init__(self, estimator: RobustStateEstimator):
        self.estimator = estimator
        # Obtem a escala dinâmica diretamente do modelo JIT sem chumbá-las no código
        self.scale = self.estimator.model.get_scales().numpy().tolist() if self.estimator.model else [0.875, 0.675, 1.0, 2.0, 2.0, 10.0]

    def get_ppo_obs(self):
        x_est, y_est, th_est, vx, vy, vw = self.estimator.predict()
        
        # Resgata a última medição bruta no buffer para isolar o resíduo
        last_raw_x = float(self.estimator.buffer[-1, 0])
        last_raw_y = float(self.estimator.buffer[-1, 1])
        last_raw_th = math.atan2(float(self.estimator.buffer[-1, 2]), float(self.estimator.buffer[-1, 3]))
        
        th_res = (th_est - last_raw_th + math.pi) % (2 * math.pi) - math.pi
        
        return (
            (x_est - last_raw_x) / self.scale[0],
            (y_est - last_raw_y) / self.scale[1],
            th_res / self.scale[2],
            vx / self.scale[3],
            vy / self.scale[4],
            vw / self.scale[5]
        )