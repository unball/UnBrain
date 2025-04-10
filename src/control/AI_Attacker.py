from control import Control
import time
import torch
import sys
sys.path.append("..")
from ML_algorithms.PPO import PPO


class AI_Control(Control):
    def __init__(self, world, env, observation):
        Control.__init__(self, world)
        self.model = None
        self.env = env
        self.observation = observation
        self.time = time.time() - 1/60
        self.v_wheel0 = 0
        self.v_wheel1 = 0

    def output(self, robot):
        if self.model is None:
            self.model = PPO(self.env)
            self.model.load_model("src/strategy/entity/ppo_models_behind_ball_24")
        actions, _ = self.model.get_action(torch.tensor(self.observation, dtype=torch.float, device=self.model.device))
        if time.time() - self.time > 0.02:
            self.observation = self.env.step(actions.cpu())
            self.time = time.time()
            self.v_wheel0, self.v_wheel1 = self.env._actions_to_v_wheels(actions.cpu())
            
        return self.v_wheel0, self.v_wheel1