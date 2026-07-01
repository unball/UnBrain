import numpy as np
import time
from strategy.entity.AI_attacker import AI_Attacker
from tools import norm

class AI_AttackerTester(AI_Attacker):
    def __init__(self, world, robot):
        super().__init__(world, robot)
        self.state = 9 # Mesmo estado inicial do ControlTesterRobust original
        self.target = np.array([0.0, 0.0])

        with open("trajectory.csv", "a") as f:
            f.write("time,state,x,y,th\n")

        # Intercepta a observação para enganar a IA e fazê-la ir para o waypoint
        self.original_get_obs = self.env._get_observation
        
        def mock_get_observation():
            obs = self.original_get_obs()
            c = -1 if self.env.enemy_AI else 1
            obs[0] = self.env.norm_pos(c * self.target[0])
            obs[1] = self.env.norm_pos(self.target[1])
            obs[2] = self.env.norm_v(0.0)
            obs[3] = self.env.norm_v(0.0)
            return obs
            
        self.env._get_observation = mock_get_observation

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        
        t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
        with open("trajectory.csv", "a") as f:
            f.write(f"{t:.4f},{self.state},{rr[0]},{rr[1]},{rr[2]}\n")

        # Define os waypoints (cantos da quadra, como no Tester original)
        if self.state == 9:
            self.target = np.array([-0.375, 0.430])
        elif self.state == 10:
            self.target = np.array([0.375, 0.430])
        elif self.state == 11:
            self.target = np.array([0.375, -0.430])
        elif self.state == 12:
            self.target = np.array([-0.375, -0.430])
        else:
            self.target = np.array([0.0, 0.0])

        # Verifica se chegou
        if norm(rr[:2], self.target) < 0.05:
            if self.state < 12:
                self.state += 1
            else:
                print("[CALIBRATOR] AI_Attacker: Volta completa nos waypoints!", flush=True)
                self.state = 9

    def directionDecider(self):
        pass # IA lida com a própria cinemática, não forçamos direção vetorial.
