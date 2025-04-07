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



class Env():
    def __init__(self, world, robot_id):
        self.world = world  # Referência direta ao mundo
        self.robot_id = robot_id # ID do robô
        
        # Espaço de ação: controle das rodas do robô azul 0
        self.action_space = Box(low=-1, high=1, shape=(2,), dtype=np.float32)

        # Espaço de observação: estado normalizado [-1.25, 1.25]
        self.observation_space = Box(low=-1.25, high=1.25, shape=(40,), dtype=np.float32)

    def step(self, action):
        """
        Lê o estado atualizado do world e retorna a observação.
        """
        next_observation = self._get_observation()
        return next_observation  # Sem reward e done

    def _get_observation(self):
        """
        Converte o estado do world em um vetor de observação.
        """
        obs = np.zeros(40)  # Vetor de observação

        # 🔹 1. Informações da bola
        obs[0:4] = np.array([
            self.world.ball.x,
            self.world.ball.y,
            self.world.ball.vx,
            self.world.ball.vy
        ])

        # 🔹 2. Informações dos robôs aliados (no treinamento. os azuis)
        allied_team = self.world.team
        for robot in allied_team:
            if robot.id == self.robot_id:
                allied_team.remove(robot)
                allied_team.insert(0, robot) # define o primeiro do time como o robô de IA_attacker em questão

        for i in range(3):  # três robôs do time aliado
            base = 4 + (7 * i)
            
            obs[base:base+7] = np.array([
                allied_team[i].x,
                allied_team[i].y,
                np.sin(allied_team[i].th),
                np.cos(allied_team[i].th),
                allied_team[i].vx,
                allied_team[i].vy,
                allied_team[i].thvec
            ])

        # 🔹 3. Informações dos robôs inimigos (no treinamento, os amarelos)
        for i in range(3):  # três robôs do time adversário
            base = 25 + (5 * i)
            obs[base:base+5] = np.array([
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ])

        return obs
    

class AI_Attacker(Entity):
    def __init__(self, world, robot):
        Entity.__init__(self, world, robot)
        self.robot = robot
        self.env = Env(world, robot.id)
        self._control = AI_Control(world, self.env)

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



class AI_Control(Control):
    def __init__(self, world, env):
        Control.__init__(self, world)
        self.model = None
        self.env = env

    def output(self, robot, obs):
        if self.model is None:
            self.model = self.load_model_PPO() # TODO: colocar os argumentos
        actions, _ = self.model.get_action(torch.tensor(obs, dtype=torch.float, device=DEVICE))
        actions = actions.cpu().numpy()
        return actions[0], actions[1]
    
    def load_model_PPO(self, directory, actor_filename="actor.pth", critic_filename="critic.pth"):
        obs_dim = self.env.observation_space.shape[0]
        act_dim = self.env.action_space.shape[0]
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