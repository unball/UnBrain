import gymnasium as gym
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from world import World
from strategy.entity.midfielder import Midfielder
from strategy.entity.SecAttacker import SecAttacker
from tools import sat

class EntitiesGymWrapper(gym.Wrapper):
    """
    Wrapper que intercepta o gym.step, atualiza o mundo virtual (UnBall World)
    com os dados do rSoccer, roda as entidades clássicas (Midfielder, SecAttacker)
    e combina a ação do PPO (Robô 0) com as velocidades clássicas (Robôs 1 e 2).
    """
    def __init__(self, env):
        super().__init__(env)
        
        # Inicializa o mundo padrão do UnBall
        self.world = World(n_robots=[0, 1, 2], side=1, team_yellow=False, simulado=True)
        
        # O PPO controlará o world.team[0].
        # As entidades controlam world.team[1] e world.team[2].
        self.midfielder = Midfielder(self.world, self.world.team[1])
        self.world.team[1].entity = self.midfielder
        self.world.team[1].turnOn()
        
        self.sec_attacker = SecAttacker(self.world, self.world.team[2])
        self.world.team[2].entity = self.sec_attacker
        self.world.team[2].turnOn()

    def step(self, action, *args, **kwargs):
        # action = [v_l0, v_r0] do PPO. Precisamos de [v_l0, v_r0, v_l1, v_r1, v_l2, v_r2]
        # Pega o frame atual ANTES de dar o passo (o environment original nos dá o frame no env.frame)
        if hasattr(self.env.unwrapped, 'frame'):
            frame = self.env.unwrapped.frame
            
            # Atualiza a bola
            self.world.ball.update_element(
                frame.ball.x, frame.ball.y, 
                frame.ball.v_x, frame.ball.v_y, 0
            )
            
            # Atualiza Robôs Aliados
            for i in range(3):
                if i < len(frame.robots_blue) and self.world.team[i] is not None:
                    rb = frame.robots_blue[i]
                    th_rad = np.deg2rad(rb.theta)
                    self.world.team[i].update_element(
                        rb.x, rb.y,
                        rb.v_x, rb.v_y, rb.v_theta,
                        raw_th=th_rad
                    )
            
            # Atualiza Inimigos
            for i in range(3):
                if i < len(frame.robots_yellow) and self.world.enemies[i] is not None:
                    ry = frame.robots_yellow[i]
                    th_rad = np.deg2rad(ry.theta)
                    self.world.enemies[i].update_element(
                        ry.x, ry.y,
                        ry.v_x, ry.v_y, ry.v_theta,
                        raw_th=th_rad
                    )
                    
        # Roda a lógica das Entidades Clássicas
        vl1, vr1 = 0, 0
        vl2, vr2 = 0, 0
        
        if self.world.team[1].entity:
            self.world.team[1].entity.directionDecider()
            self.world.team[1].entity.fieldDecider()
            vl1, vr1 = self.world.team[1].entity.control.actuateSimu(self.world.team[1])
            
        if self.world.team[2].entity:
            self.world.team[2].entity.directionDecider()
            self.world.team[2].entity.fieldDecider()
            vl2, vr2 = self.world.team[2].entity.control.actuateSimu(self.world.team[2])
        
        # O actuateSimu retorna velocidades das rodas em rad/s.
        # Precisamos converter para a escala [-1.0, 1.0] usada pelo action_space do vss_gym.
        max_rad_s = (440.0 / 60.0) * 2 * np.pi
        
        vl1 /= max_rad_s
        vr1 /= max_rad_s
        vl2 /= max_rad_s
        vr2 /= max_rad_s
        
        # Dependendo do rSoccer, a action list precisa ser flat
        combined_action = np.array([action[0], action[1], vl1, vr1, vl2, vr2])
        # clip just to be safe
        combined_action = np.clip(combined_action, -1.0, 1.0)
        
        return self.env.step(combined_action, *args, **kwargs)
