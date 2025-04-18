from control import Control
import time
import torch
import sys
sys.path.append("..")
from ML_algorithms.PPO import PPO


class AI_Control(Control):
        
    model = None

    def __init__(self, world, env, observation):
        Control.__init__(self, world)
        self.env = env
        self.observation = observation
        self.time = 0
        self.v_wheel0 = 0
        self.v_wheel1 = 0
        if AI_Control.model is None:
            AI_Control.model = PPO(self.env)
            AI_Control.model.load_model("src/strategy/entity/ppo_models_behind_ball_24")

    def output(self, robot):
        actions, _ = AI_Control.model.get_action(torch.tensor(self.observation, dtype=torch.float, device=AI_Control.model.device))
        if time.time() - self.time > 1/120:
            self.observation = self.env.step(actions.cpu())
            self.time = time.time()
            self.v_wheel0, self.v_wheel1 = self.env._actions_to_v_wheels(actions.cpu())
            
        return self.v_wheel0, self.v_wheel1