from model.paramsPattern import ParamsPattern
from controller.world.robot import Robot
from controller.world.ball import Ball
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
    ParamsPattern.__init__(self, "worldConfig", {
      "UVF_r": 0.05,
      "UVF_Kr": 15,
      "UVF_Kr_single": 0.1,
      "UVF_horRepSize": 0.05,
      "UVF_horMinDist": 0.1,
      "UVF_verRepSize": 0.15,
      "UVF_verGoalSize": 0.2,
      "UVF_verMinDist": 0.15,
      "UVF_ponRadius": 0.3,
      "UVF_ponDistanceRadius": 0.1,
      "UVF_ponMinAvoidanceAngle": 0.5
    })

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
    self.__referenceTime = 0
    self.dt = 0
    
  def update(self, visionMessage):
    """Recebe uma mensagem da visão e atualiza as posições e velocidades de robôs e bola"""
  
    # Atualiza cada robô localizado e identificado
    for i,allyPose in enumerate(visionMessage.allyPoses):
      if not allyPose[3]: continue
      
      # O ângulo do robô não pode variar de um loop para outro mais que 70% de pi/2, se isso ocorrer deve ser algum erro da visão
      # if self.robots[i].poseDefined and np.arccos(np.cos(allyPose[2]-self.robots[i].th)) > 0.49*np.pi/2:
      #   theta = self.robots[i].th
      # else:
      theta = allyPose[2]
      
      self.robots[i].raw_update(allyPose[0], allyPose[1], theta)

    # Atualiza a lista de robôs adversários
    self.enemyRobots = visionMessage.advPos
    
    # Atualiza a bola se ela foi localizada
    if visionMessage.ball_found:
      self.ball.raw_update(visionMessage.ball_x, visionMessage.ball_y)
    
    # Computa a velocidade com base no tempo passado desde a última chamada a `update` e atualiza o tempo para o tempo atual.
    self.dt = time.time() - self.__referenceTime
    self.calc_velocities(self.dt)
    self.__referenceTime = time.time()
    
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