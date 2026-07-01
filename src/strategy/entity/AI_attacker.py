from ..entity import Entity

from tools import adjustAngle

from control.AI_Attacker import AI_Control

import numpy as np

try:
    from gymnasium.spaces import Box
except ImportError:
    from gym.spaces import Box


class AI_Attacker(Entity):
    def __init__(self, world, robot):
        Entity.__init__(self, world, robot)
        self.robot = robot
        self.env = Env(world, robot.id, world.enemy_AI)
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
        pass

    def isLocked(self):
        return False


class Env():
    def __init__(self, world, robot_id, enemy_AI):
        self.world = world  # Referência direta ao mundo
        self.robot_id = robot_id # ID do robô
        self.NORM_BOUNDS = 1.2
        self.enemy_AI = enemy_AI
        
        # Espaço de ação: controle das rodas do robô azul 0
        self.action_space = Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        
        # Espaço de observação: estado normalizado [-1.25, 1.25]
        self.observation_space = Box(low=-self.NORM_BOUNDS, high=self.NORM_BOUNDS, shape=(40,), dtype=np.float32)

        self.field_params ={'rbt_motor_max_rpm': 440.0, 'goal_width': 0.4, 'ball_radius': 0.0215, 'penalty_width': 0.7, 'rbt_wheel_radius': 0.026, 'goal_depth': 0.1,
        'rbt_kicker_width': -1.0, 'penalty_length': 0.15, 'length': 1.5, 'rbt_distance_center_kicker': -1.0, 'rbt_kicker_thickness': -1.0, 
        'width': 1.3, 'rbt_wheel0_angle': 90.0, 'rbt_wheel1_angle': 270.0, 'rbt_wheel2_angle': -1.0, 'rbt_wheel3_angle': -1.0, 'rbt_radius': 0.0375}
        max_wheel_rad_s = (self.field_params['rbt_motor_max_rpm'] / 60) * 2 * np.pi
        self.max_v = max_wheel_rad_s * self.field_params['rbt_wheel_radius']
        # 0.04 = robot radius (0.0375) + wheel thicknees (0.0025)
        self.max_w = np.rad2deg(self.max_v / 0.04)

        self.v_wheel_deadzone = 0.05
        self.max_pos = max(self.field_params['width'] / 2, (self.field_params['length'] / 2) + self.field_params['penalty_length'])

    def step(self, action):
        """
        Lê o estado atualizado do world e retorna a observação.
        """
        # action manda para o get_commands, que transforma pra v_wheels e envia o comando pro simulador

        next_observation = self._get_observation()
        return next_observation  # Sem reward e done

    def _actions_to_v_wheels(self, actions):
        # Scale actions to max wheel speed in rad/s
        v_0 = np.clip(actions[0] * self.max_v, -self.max_v, self.max_v)
        v_1 = np.clip(actions[1] * self.max_v, -self.max_v, self.max_v)
        
        # Convert to rad/s
        v_0 /= self.field_params['rbt_wheel_radius']
        v_1 /= self.field_params['rbt_wheel_radius']
        
        # Lógica de Espelhamento Cinemático:
        # Se estamos fisicamente no lado direito (side = -1), a roda esquerda
        # do mundo refletido corresponde à roda direita do mundo real!
        # A flag enemy_AI também inverte a perspectiva.
        effective_side = self.world.field.side * (-1 if self.enemy_AI else 1)
        
        if effective_side == -1:
            # O mundo real está espelhado, então as rodas trocam de lugar
            left_wheel_speed = v_1
            right_wheel_speed = v_0
        else:
            left_wheel_speed = v_0
            right_wheel_speed = v_1
            
        return left_wheel_speed, right_wheel_speed

    def _get_observation(self):
        """
        Converte o estado do world em um vetor de observação.
        """
        obs = np.zeros(40)  # Vetor de observação
        if self.enemy_AI: c = -1 
        else: c = 1
            

        # 🔹 1. Informações da bola
        obs[0:4] = np.array([
            self.norm_pos(c*self.world.ball.x),
            self.norm_pos(self.world.ball.y),
            self.norm_v(c*self.world.ball.vx),
            self.norm_v(self.world.ball.vy)
        ])

        # 🔹 2. Informações dos robôs aliados (no treinamento. os azuis)
        allied_team = self.world.team.copy()
        for robot in allied_team:
            if robot is not None:
                if robot.id == self.robot_id:
                    allied_team.remove(robot)
                    allied_team.insert(0, robot) # define o primeiro do time como o robô de IA_attacker em questão

        for i in range(3):  # três robôs do time aliado
            if i == 0:
                base = 4 + (7 * i)
                
                obs[base:base+7] = np.array([
                    self.norm_pos(c*allied_team[i].x),
                    self.norm_pos(allied_team[i].y),
                    np.sin(adjustAngle((np.pi - allied_team[i].th))) if c == -1 else np.sin((allied_team[i].th)),
                    np.cos(adjustAngle((np.pi - allied_team[i].th))) if c == -1 else np.cos((allied_team[i].th)),
                    self.norm_v(c*allied_team[i].vx),
                    self.norm_v(allied_team[i].vy),
                    self.norm_w(c*np.rad2deg(allied_team[i].w))
                ])
            else:
                base = 4 + (7 * i)
                
                obs[base:base+7] = np.array([
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0
                    ])

        # 🔹 3. Informações dos robôs inimigos (no treinamento, os amarelos)
        # A observação só expõe os slots de inimigo que o MODELO está acostumado a ver:
        #   - train_n_enemies: com quantos inimigos a rede foi treinada (detectado no load).
        #   - episode_n_enemies: quantos inimigos estão fisicamente no campo agora.
        # Preenche o min dos dois e zera o resto (modelo 1v1 nunca recebe inimigos; 1v3 recebe 3).
        # Se train_n_enemies for None (não inferível), assume o comportamento de treino padrão
        # (sem inimigos na obs) para não introduzir shift de distribuição inadvertido.
        train_n_enemies = getattr(self, 'train_n_enemies', None)
        if train_n_enemies is None:
            train_n_enemies = 0
        n_ep_enemies = getattr(self.world, 'episode_n_enemies', 0)
        n_visible = min(train_n_enemies, n_ep_enemies)
        for i in range(3):
            base = 25 + (5 * i)
            enemy = self.world.enemies[i] if i < len(self.world.enemies) else None
            if i < n_visible and enemy is not None:
                obs[base:base+5] = np.array([
                    self.norm_pos(c * enemy.x),
                    self.norm_pos(enemy.y),
                    self.norm_v(c * enemy.vx),
                    self.norm_v(enemy.vy),
                    self.norm_w(np.rad2deg(enemy.w))
                ])
            else:
                obs[base:base+5] = 0.0

        return np.array(obs, dtype=np.float32)
    
    def norm_pos(self, pos):
        return np.clip(pos / self.max_pos, -self.NORM_BOUNDS, self.NORM_BOUNDS)

    def norm_v(self, v):
        return np.clip(v / self.max_v, -self.NORM_BOUNDS, self.NORM_BOUNDS)

    def norm_w(self, w):
        return np.clip(w / self.max_w, -self.NORM_BOUNDS, self.NORM_BOUNDS)