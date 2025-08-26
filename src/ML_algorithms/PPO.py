import torch
import torch.nn as nn
from torch.distributions import MultivariateNormal
from torch.optim import Adam
import torch.nn.functional as F
import numpy as np

import os
import time

torch.manual_seed(5)
torch.cuda.manual_seed_all(5)


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

    def load_model(self, directory, ppo_filename="ppo_full_checkpoint.pth"):
        ppo_path = os.path.join(directory, ppo_filename)
        if os.path.exists(ppo_path):
            checkpoint = torch.load(os.path.join(directory, ppo_filename), map_location=self.device)
            self.actor.load_state_dict(checkpoint['actor'])
            self.critic.load_state_dict(checkpoint['critic'])
            self.actor_optim.load_state_dict(checkpoint['actor_optim'])
            self.critic_optim.load_state_dict(checkpoint['critic_optim'])
            self.log_std = checkpoint['log_std']

            print(f"Models loaded from {directory} ppo_full_checkpoint")
        else:
            print(f"Model files not found in {directory} ppo_full_checkpoint")
        # else:
        #     actor_path = os.path.join(directory, "actor.pth")
        #     critic_path = os.path.join(directory, "critic.pth")
        #     if os.path.exists(actor_path) and os.path.exists(critic_path):
        #         self.actor.load_state_dict(torch.load(actor_path, map_location=self.device))
        #         self.critic.load_state_dict(torch.load(critic_path, map_location=self.device))
        #         print(f"Models loaded from {directory}")
        #     else:
        #         print(f"Model files not found in {directory}")

    def _init_hyperparameters(self, hyperparams):
        # Default values got using optuna
        defaults = {
            'timesteps_per_batch': 1200,
            'max_timesteps_per_episode': 1200,
            'n_updates_per_iteration': 4, 
            'lr': 0.0003,
            'gamma': 0.867218,
            'clip': 0.2,
            'lam': 0.997752,
            'num_minibatches': 64,
            'ent_coef': 0.01,
            'target_kl': 0.02,
            'max_grad_norm': 0.5
        }
        # Override with provided hyperparams
        for key, value in defaults.items():
            if hyperparams is not None and hyperparams.get(key): defaults[key] = hyperparams[key]
            setattr(self, key, hyperparams.get(key) if hyperparams is not None and hyperparams.get(key) else value)

    def get_action(self, obs):
        with torch.no_grad():
            mean = self.actor(obs)
            std = torch.exp(self.log_std)
            dist = MultivariateNormal(mean, covariance_matrix=torch.diag(std))
            action = dist.sample()
            log_prob = dist.log_prob(action)
            return action.detach(), log_prob.detach()
    
class FeedForwardNN(nn.Module):
    def __init__(self, in_dim, out_dim):
        super(FeedForwardNN, self).__init__()
        self.layer1 = nn.Linear(in_dim, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, out_dim)
        
        # Get device from model parameters
        self.device = next(self.parameters()).device

    def forward(self, obs, device= "cuda"):
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