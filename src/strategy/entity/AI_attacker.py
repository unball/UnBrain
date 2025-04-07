from control import Control
from ..entity import Entity

import torch
from network import FeedForwardNN
import os
import numpy as np

DEVICE = "cpu"

class Box:
    def __init__(self, low, high, shape, dtype=np.float32):
        """
        Inicializa o espaço contínuo.

        :param low: Valor mínimo permitido (float, int ou array)
        :param high: Valor máximo permitido (float, int ou array)
        :param shape: Formato do espaço (ex: (3,) para 3 variáveis)
        :param dtype: Tipo de dado (padrão: np.float32)
        """
        self.low = np.full(shape, low, dtype=dtype) if np.isscalar(low) else np.array(low, dtype=dtype)
        self.high = np.full(shape, high, dtype=dtype) if np.isscalar(high) else np.array(high, dtype=dtype)
        self.shape = shape
        self.dtype = dtype

    def sample(self):
        """Gera uma amostra aleatória dentro dos limites do espaço."""
        return np.random.uniform(self.low, self.high).astype(self.dtype)

    def contains(self, x):
        """Verifica se um valor está dentro do espaço."""
        x = np.array(x, dtype=self.dtype)
        return x.shape == self.shape and np.all(x >= self.low) and np.all(x <= self.high)

    def __repr__(self):
        return f"Box(low={self.low}, high={self.high}, shape={self.shape}, dtype={self.dtype})"

class AI_Attacker(Entity):
    def __init__(self, world, robot):
        Entity.__init__(self, world, robot)
        self.robot = robot
        self.env = Env(world)
        self._control = AI_Control(world)

    @property
    def control(self):
        return self._control
    
    def fieldDecider(self):
        # 1. Verificar se existe e a env
        # 2. Se existe:
        # 3.     Atualizar o observation
        # 4.     Realizar um step
        # 5. Se não existe:
        # 6.     Criar a env
        # 7.     Atualizar o observation
        # 8.     Realizar um step
        # 9. Atualizar o control com o resultado do step
        pass

    def directionDecider(self):
        # não será usado
        pass

    def equalsTo(self, otherEntityOfSameClass):
        return self.robot == otherEntityOfSameClass.robot

    def onExit(self):
        self.isLocked = False

    def isLocked(self):
        return False



def load_model_PPO(directory, actor_filename="actor.pth", critic_filename="critic.pth"):
    env = get_env()
    obs_dim = env.observation_space.shape[0]
    act_dim = env.action_space.shape[0]
    actor = FeedForwardNN(obs_dim, act_dim).to(DEVICE)
    critic = FeedForwardNN(obs_dim, 1).to(DEVICE)
    actor_path = os.path.join(directory, actor_filename)
    critic_path = os.path.join(directory, critic_filename)
    if os.path.exists(actor_path) and os.path.exists(critic_path):
        actor.load_state_dict(torch.load(actor_path, map_location=DEVICE))
        critic.load_state_dict(torch.load(critic_path, map_location=DEVICE))
        print(f"Models loaded from {directory}")
    else:
        print(f"Model files not found in {directory}")



class AI_Control(Control):
    def __init__(self, world):
        Control.__init__(self, world)
        self.model = None
        self.observation = None

    def output(self, robot, obs):
        if self.model is None:
            self.model = load_model_PPO() # TODO: colocar os argumentos
        actions, _ = self.model.get_action(torch.tensor(obs, dtype=torch.float, device=DEVICE))
        actions = actions.cpu().numpy()
        return actions[0], actions[1]