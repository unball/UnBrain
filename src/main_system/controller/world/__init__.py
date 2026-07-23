from main_system.model.paramsPattern import ParamsPattern
from main_system.controller.world.robot import Robot
from main_system.controller.world.ball import Ball
from main_system.model import Model
import time
import numpy as np

class Field():
  LEFT = -1
  """Lado aliado está a esquerda"""
  
  RIGHT = 1
  """Lado aliado está a direita"""

class World(ParamsPattern):
  """Classe de mundo que armazena as posições dos robôs, velocidades, posição da bola, limites de campo e escore de jogo."""
  
  def __init__(self, n_robots):
    # Variáveis REAIS do UVF do runtime UnBrain (src/strategy/field/UVF.py), com os
    # valores padrão do artigo. Editar aqui sobrepõe o campo real via hlc_uvf_overrides.
    ParamsPattern.__init__(self, "worldConfig", {
      "UVF_radius": 0.1382,      # self.r  — raio da espiral
      "UVF_Kr": 0.2333,          # self.Kr — constante da espiral
      "UVF_Ko": 0.0003,          # self.Ko — ganho do desvio de obstáculo
      "UVF_dmin_wall": 0.0274,   # dmin[0] — distância mínima da parede
      "UVF_dmin_robot": 0.0444,  # dmin[1:] — distância mínima dos robôs
      "UVF_delta_wall": 51.0,    # delta[0] — nitidez do desvio de parede
      "UVF_delta_robot": 90.0,   # delta[1:] — nitidez do desvio dos robôs
      "UVF_delta_b": 2483.0,     # delta_b — nitidez da mistura com o alvo
    }, deferred=True)


    self.vision_noise_params = ParamsPattern("visionNoise", {
      "pg_noise_enabled": False,
      "pg_noise_std_base": 0.01,
      "pg_noise_std_scale": 0.005,
      "ge_dropout_enabled": False,
      "ge_p": 0.05,
      "ge_q": 0.2,
      "ge_eg": 0.01,
      "ge_eb": 0.9,
      "outlier_enabled": False,
      "outlier_prob": 0.01,
      "outlier_range": 1.0,
      "domain_randomization_enabled": False,
      "pg_noise_std_base_min": 0.001,
      "pg_noise_std_base_max": 0.05,
      "pg_noise_std_scale_min": 0.001,
      "pg_noise_std_scale_max": 0.02,
      "ge_p_min": 0.01,
      "ge_p_max": 0.2,
      "ge_q_min": 0.1,
      "ge_q_max": 0.5,
      "ge_eg_min": 0.0,
      "ge_eg_max": 0.05,
      "ge_eb_min": 0.8,
      "ge_eb_max": 1.0,
      "outlier_prob_min": 0.001,
      "outlier_prob_max": 0.05,
      "outlier_range_min": 0.5,
      "outlier_range_max": 2.0,
      "domain_randomization_interval": 5000,
      "apply_to_ball": True,
      "apply_to_robot_0": True,
      "apply_to_robot_1": True,
      "apply_to_robot_2": True,
    }, deferred=True)

    self.field_x_length = 1.75
    self.field_y_length = 1.35
    self.xmax = (self.field_x_length) / 2
    self.ymax = (self.field_y_length) / 2
    self.xmaxmargin = self.xmax - 0.10
    self.ymaxmargin = self.ymax - 0.20
    self.marginLimits = (self.xmaxmargin, self.ymaxmargin)
    self.goalpos = (self.xmax, 0)
    self.allyGoalPos = np.array([-self.xmax, 0])
    self.rg = np.array([-0.75, 0])
    self.goalAreaSize = np.array([0.3, 0.4])
    self.goalylength = 0.4
    self.n_robots = n_robots
    self.fieldSide = Field.RIGHT
    self.running = False
    self.checkBatteries = False
    self.manualControlSpeedV = 0
    self.manualControlSpeedW = 0
    self.mus = [0.07, 0.07, 0.12, 0.07, 0.07]
    self.robots = [Robot(self, i, self.mus[i]) for i in range(self.n_robots)]
    self.enemyRobots = []
    self.edges = []
    self.ball = Ball(self)
    self.force_entities = Model().getValue("force_entities", {})
    if self.force_entities is None:
        self.force_entities = {}
    self.__referenceTime = 0
    self.dt = 0
    self.updateCount = 0

    self._team_yellow = Model().getValue("team_yellow", True)

  @property
  def team_yellow(self):
    return self._team_yellow
    
  @team_yellow.setter
  def team_yellow(self, value):
    self._team_yellow = value
    # Persistência diferida: só grava no disco quando o usuário confirmar no botão salvar.
    Model().setDeferred("team_yellow", value)
    
  def update(self, visionMessage):
    """Recebe uma mensagem da visão e atualiza as posições e velocidades de robôs e bola"""
    if time.time() - getattr(self, 'last_rsoccer_time', 0) < 1.0: return
  
    # Atualiza cada robô localizado e identificado
    for i,allyPose in enumerate(visionMessage.allyPoses):
      if not allyPose[3]: continue
      
      # Gate de posição: rejeita só saltos irreais (>1.5m). O gate de ÂNGULO
      # foi removido: ele descartava qualquer medição de theta que diferisse
      # >44° do valor JÁ ARMAZENADO e mantinha o antigo — como comparava sempre
      # contra o valor guardado, um único frame ruim travava o ângulo para
      # sempre (medições seguintes passavam a diferir >44° do valor preso e
      # eram rejeitadas). Era a causa direta de "a camisa fica fixa enquanto o
      # robô gira". A robustez do ângulo agora vem da FONTE (detectarTime usa o
      # eixo do retângulo da camisa), não de um gate que trava. O unwrapping
      # contínuo do ângulo é feito em Element.raw_update.
      if self.robots[i].poseDefined:
          dist = np.hypot(allyPose[0] - self.robots[i].x, allyPose[1] - self.robots[i].y)
          if dist > 1.50:
              continue  # Salto irreal (>1.5m): pula a medição. (Era 0.30, mas impedia de mover o robô com a mão)

      self.robots[i].raw_update(allyPose[0], allyPose[1], allyPose[2])

    # Atualiza a lista de robôs adversários
    self.enemyRobots = visionMessage.advPos
    
    # Atualiza a bola se ela foi localizada
    if visionMessage.ball_found:
      self.ball.raw_update(visionMessage.ball_x, visionMessage.ball_y)
    
    # Computa a velocidade com base no tempo passado desde a última chamada a `update` e atualiza o tempo para o tempo atual.
    self.dt = time.time() - self.__referenceTime
    self.calc_velocities(self.dt)
    self.__referenceTime = time.time()

  def update_from_state(self, state_msg):
    """Atualiza o mundo diretamente de um dicionário (recebido via rede do UnBrain simulador)"""
    if time.time() - getattr(self, 'last_rsoccer_time', 0) < 1.0: return
    # Atualiza bola
    ball = state_msg.get("ball", {})
    if "pos_x" in ball and "pos_y" in ball:
        self.ball.raw_update(ball["pos_x"], ball["pos_y"])
        
    # Atualiza robôs
    robots = state_msg.get("robots", {})
    for i_str, r in robots.items():
        i = int(i_str)
        if i < self.n_robots:
            self.robots[i].raw_update(r["pos_x"], r["pos_y"], r["th"])
            self.robots[i].dir = r.get("dir", 1)
            
    # Atualiza inimigos
    enemies = state_msg.get("enemies", {})
    self.enemyRobots = []
    for i_str, e in enemies.items():
        self.enemyRobots.append((e["pos_x"], e["pos_y"]))
        
    self.episode_testing_running = state_msg.get("episode_testing_running", False)

    # [HLC] Grade do campo vetorial amostrada pelo UnBrain (None quando desligado).
    self.hlc_uvf_grid = state_msg.get("uvf_grid", None)

    self.updateCount += 1
    # Update world from UnBrain state, but DO NOT update self.running!
    # MainSystem is the master of UI states, so it should not inherit running, team_yellow, or fieldSide from UnBrain
    
    self.dt = time.time() - self.__referenceTime
    self.calc_velocities(self.dt)
    self.__referenceTime = time.time()

  def update_from_rsoccer(self, message):
    """Atualiza a renderização com base nos estados do rsoccer passados do AI worker"""
    self.last_rsoccer_time = time.time()
    bx = message['ball'].get('x', 0)
    by = message['ball'].get('y', 0)
    self.ball.raw_update(bx, by)

    if self.team_yellow:
        my_team = message.get('robots_yellow', [])
        enemies = message.get('robots_blue', [])
    else:
        my_team = message.get('robots_blue', [])
        enemies = message.get('robots_yellow', [])

    for r_dict in my_team:
        r_id = r_dict['id']
        if r_id < len(self.robots):
            self.robots[r_id].raw_update(r_dict['x'], r_dict['y'], r_dict['theta'])

    self.enemyRobots = []
    for r_dict in enemies:
        self.enemyRobots.append({
            'x': r_dict['x'], 
            'y': r_dict['y'], 
            'theta': r_dict.get('theta', 0),
            'id': r_dict.get('id', 0)
        })

    self.updateCount += 1

  def setRunning(self, state):
    """Recebe uma flag `state` indicando se o jogo está ou não rodando."""
    self.running = state
    if state is True:
      for robot in self.robots:
        robot.lastTimeAlive = time.time()
        robot.spin = 0
    
  def getRobots(self):
    """Retorna os robôs."""
    return self.robots
    
  def calc_velocities(self, dt):
    """Computa as velocidades para robôs e bola com base em suas posições anteriores e atuais e com base no intervalo de tempo `dt`."""
    for robot in self.robots:
      robot.calc_velocities(dt)
    
    self.ball.calc_velocities(dt)

  def setEdges(self, points):
    self.edges = points

  def setFieldSide(self, side):
    self.fieldSide = side

  def setPreferedEntity(self, robotIndex, entityPref):
    self.robots[robotIndex].preferedEntity = entityPref
    if entityPref is not None and entityPref != "None":
        self.force_entities[str(robotIndex)] = entityPref
    else:
        if str(robotIndex) in self.force_entities:
            del self.force_entities[str(robotIndex)]
    # Persistência diferida: só grava no disco quando confirmar no botão salvar.
    Model().setDeferred("force_entities", self.force_entities)

  def get_vision_noise_config(self):
    return self.vision_noise_params.params

  def set_noise_param(self, key, value):
    self.vision_noise_params.setParam(key, value)
    self.send_noise_config_to_loop()

  def send_noise_config_to_loop(self):
    import socket
    import json
    try:
      config = self.get_vision_noise_config()
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.sendto(json.dumps(config).encode('utf-8'), ('127.0.0.1', 20022))
      sock.close()
    except Exception as e:
      print("Warning: failed to send noise config to loop:", e)
