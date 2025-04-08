import time
from control import Control
from ..entity import Entity

import torch
import os
import numpy as np
import torch.nn as nn
import optuna
from torch.distributions import MultivariateNormal
from torch.optim import Adam
import torch.nn.functional as F

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
        # action manda para o get_commands, que transforma pra v_wheels e envia o comando pro simulador

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
        allied_team = self.world.team.copy()
        for robot in allied_team:
            if robot.id == self.robot_id:
                allied_team.remove(robot)
                allied_team.insert(0, robot) # define o primeiro do time como o robô de IA_attacker em questão

        for i in range(3):  # três robôs do time aliado
            base = 4 + (7 * i)
            
            obs[base:base+7] = np.array([
                allied_team[i].x,
                allied_team[i].y,
                np.sin(allied_team[i].th_raw),
                np.cos(allied_team[i].th_raw),
                allied_team[i].vx,
                allied_team[i].vy,
                allied_team[i].w_raw
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
        self.observation = self.env._get_observation()
        self._control = AI_Control(world, self.env, self.observation)

    @property
    def control(self):
        return self._control
    
    def fieldDecider(self):
        # não será usado
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
    def __init__(self, world, env, observation):
        Control.__init__(self, world)
        self.model = None
        self.env = env
        self.observation = observation
        self.field_params ={'rbt_motor_max_rpm': 370.0, 'goal_width': 0.4, 'ball_radius': 0.0215, 'penalty_width': 0.7, 'rbt_wheel_radius': 0.015, 'goal_depth': 0.1,
        'rbt_kicker_width': -1.0, 'penalty_length': 0.15, 'length': 1.5, 'rbt_distance_center_kicker': -1.0, 'rbt_kicker_thickness': -1.0, 
        'width': 1.3, 'rbt_wheel0_angle': 90.0, 'rbt_wheel1_angle': 270.0, 'rbt_wheel2_angle': -1.0, 'rbt_wheel3_angle': -1.0, 'rbt_radius': 0.04}
        self.max_wheel_rad_s = (self.field_params['rbt_motor_max_rpm'] / 60) * 2 * np.pi
        self.max_v = self.max_wheel_rad_s * self.field_params['rbt_wheel_radius']
        # 0.045 = robot radius (0.04) + wheel thicknees (0.005)
        self.max_w = np.rad2deg(self.max_v / 0.045)

        self.v_wheel_deadzone = 0.05

    def output(self, robot):
        if self.model is None:
            self.model = PPO(self.env)
            self.model.load_model("PATH_TO_MODEL")
        actions, _ = self.model.get_action(torch.tensor(self.observation, dtype=torch.float, device=DEVICE))
        self.observation = self.env.step(actions.cpu())
        actions = actions.cpu().numpy()
        return self._actions_to_v_wheels(actions)
    
    def _actions_to_v_wheels(self, actions):
        left_wheel_speed = actions[0] * self.max_v
        right_wheel_speed = actions[1] * self.max_v

        left_wheel_speed, right_wheel_speed = np.clip(
            (left_wheel_speed, right_wheel_speed), -self.max_v, self.max_v
        )

        # Deadzone
        if -self.v_wheel_deadzone < left_wheel_speed < self.v_wheel_deadzone:
            left_wheel_speed = 0

        if -self.v_wheel_deadzone < right_wheel_speed < self.v_wheel_deadzone:
            right_wheel_speed = 0

        # Convert to rad/s
        left_wheel_speed /= self.field_params['rbt_wheel_radius']
        right_wheel_speed /= self.field_params['rbt_wheel_radius']

        return left_wheel_speed*10, right_wheel_speed*10





class PPO:
    def __init__(self, env, hyperparams=None, t_so_far = 0):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._init_hyperparameters(hyperparams)
        self.tempo = time.time()
        self.t_so_far = t_so_far

        # Environment information
        self.env = env
        self.obs_dim = env.observation_space.shape[0]
        self.act_dim = env.action_space.shape[0]

        # In the __init__ method of PPO
        self.log_std = nn.Parameter(torch.zeros(self.act_dim, device=self.device))

        # Actor and Critic Networks
        self.actor = FeedForwardNN(self.obs_dim, self.act_dim).to(self.device)
        self.critic = FeedForwardNN(self.obs_dim, 1).to(self.device)

        # Optimizers
        #self.actor_optim = Adam(self.actor.parameters(), lr=self.lr)
        # Update the actor optimizer to include log_std
        self.actor_optim = Adam(list(self.actor.parameters()) + [self.log_std], lr=self.lr)
        self.critic_optim = Adam(self.critic.parameters(), lr=self.lr)

        # Covariance matrix for action distribution
        self.cov_var = torch.full(size=(self.act_dim,), fill_value=0.5).to(self.device)
        self.cov_mat = torch.diag(self.cov_var).to(self.device)

    def load_model(self, directory, actor_filename="actor.pth", critic_filename="critic.pth"):
        actor_path = os.path.join(directory, actor_filename)
        print(actor_path)
        critic_path = os.path.join(directory, critic_filename)
        print(critic_path)
        if os.path.exists(actor_path) and os.path.exists(critic_path):
            self.actor.load_state_dict(torch.load(actor_path, map_location=self.device))
            self.critic.load_state_dict(torch.load(critic_path, map_location=self.device))
            print(f"Models loaded from {directory}")
        else:
            print(f"Model files not found in {directory}")

    def _init_hyperparameters(self, hyperparams):
        # Default values got using optuna
        defaults = {
            'timesteps_per_batch': 1200*3,
            'max_timesteps_per_episode': 1000,
            'n_updates_per_iteration': 4, 
            'lr': 0.005,
            'gamma': 0.9311676192882882,
            'clip': 0.28252437747027603,
            'lam': 0.9899638989806914,
            'num_minibatches': 32,
            'ent_coef': 0.0008668161954189972,
            'target_kl': 0.02,
            'max_grad_norm': 0.5
        }
        # Override with provided hyperparams
        for key, value in defaults.items():
            if hyperparams is not None and hyperparams.get(key): defaults[key] = hyperparams[key]
            setattr(self, key, hyperparams.get(key) if hyperparams is not None and hyperparams.get(key) else value)

    def calculate_gae(self, rewards, values, dones):
        batch_advantages = []
        for ep_rews, ep_vals, ep_dones in zip(rewards, values, dones):
            advantages = []
            last_advantage = 0
            for t in reversed(range(len(ep_rews))):
                if t + 1 < len(ep_rews):
                    delta = ep_rews[t] + self.gamma * ep_vals[t + 1] * (1 - ep_dones[t + 1]) - ep_vals[t]
                else:
                    delta = ep_rews[t] - ep_vals[t]
                advantage = delta + self.gamma * self.lam * (1 - ep_dones[t]) * last_advantage
                last_advantage = advantage
                advantages.insert(0, advantage)
            batch_advantages.extend(advantages)
        return torch.tensor(batch_advantages, dtype=torch.float, device=self.device)

    def rollout(self):
        # Batch data
        batch_obs = []             # batch observations
        batch_acts = []            # batch actions
        batch_log_probs = []       # log probs of each action
        batch_rews = []            # batch rewards
        batch_vals = []
        batch_dones = []
        batch_lens = []           # episodic lengths in batch

        ep_rews, ep_vals, ep_dones = [], [], []

        t = 0
        while t < self.timesteps_per_batch:
            obs = self.env.reset()[0]
            done = False
            ep_rews, ep_vals, ep_dones = [], [], []
            steps = 0
            while not done:
                t += 1
                steps += 1
                current_obs = obs
                obs_tensor = torch.tensor(current_obs, dtype=torch.float, device=self.device)
                action, log_prob = self.get_action(obs_tensor)
                val = self.critic(obs_tensor).cpu().item()
                obs, rew, terminated, truncated, _ = self.env.step(action.cpu())
                done = terminated or truncated

                batch_obs.append(current_obs)
                batch_acts.append(action)
                batch_log_probs.append(log_prob)
                ep_rews.append(rew)
                ep_vals.append(val)
                ep_dones.append(done)

            batch_lens.append(steps)
            batch_rews.append(ep_rews)
            batch_vals.append(ep_vals)
            batch_dones.append(ep_dones)

        batch_obs = torch.tensor(np.array(batch_obs), dtype=torch.float, device=self.device)
        batch_acts = torch.stack(batch_acts).to(self.device)
        batch_log_probs = torch.tensor(batch_log_probs, dtype=torch.float, device=self.device)

        return batch_obs, batch_acts, batch_log_probs, batch_rews, batch_lens, batch_vals, batch_dones

    def get_action(self, obs):
        mean = self.actor(obs)
        std = torch.exp(self.log_std)
        dist = MultivariateNormal(mean, covariance_matrix=torch.diag(std))
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.detach(), log_prob.detach()

    def evaluate(self, batch_obs, batch_acts):
        V = self.critic(batch_obs).view(-1)  # Changed from .squeeze()
        mean = self.actor(batch_obs)
        dist = MultivariateNormal(mean, self.cov_mat)
        log_probs = dist.log_prob(batch_acts)
        return V, log_probs, dist.entropy()

    
class FeedForwardNN(nn.Module):
    def __init__(self, in_dim, out_dim):
        super(FeedForwardNN, self).__init__()
        self.layer1 = nn.Linear(in_dim, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, out_dim)
        
        # Get device from model parameters
        self.device = next(self.parameters()).device

    def forward(self, obs, device= "cpu"):
        # Convert observation to tensor if it's a numpy array
        if isinstance(obs, np.ndarray):
            obs = torch.tensor(obs, dtype=torch.float32).to(device)
        elif not isinstance(obs, torch.Tensor):
            raise TypeError("Input must be numpy array or torch tensor")
            
        # Ensure tensor is on correct device and type
        obs = obs.to(device).float()
        
        activation1 = F.relu(self.layer1(obs))
        activation2 = F.relu(self.layer2(activation1))
        output = self.layer3(activation2)
        return output