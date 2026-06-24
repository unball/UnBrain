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
        self.time = 0
        self.v_wheel0 = 0
        self.v_wheel1 = 0

    def output(self, robot):
        if self.model is None:
            self.model = PPO(self.env)
            robot.direction = 1
            self.observation = self.env._get_observation()
            self.model.load_model(directory="/home/maranhas/UnBall/Attacker-AI-Training/PPO/ppo_models/selfplay_1v1_&_1v2_curriculum_learning")
        self.observation = self.env._get_observation()
        robot.direction = 1
        actions, _ = self.model.get_action(self.observation)
        self.observation = self.env.step(actions.cpu().numpy())
        self.v_wheel0, self.v_wheel1 = self.env._actions_to_v_wheels(actions.cpu().numpy())
            
        return self.v_wheel0, self.v_wheel1