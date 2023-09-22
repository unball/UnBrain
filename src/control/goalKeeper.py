from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class GoalKeeperControl(Control):
  """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
  def __init__(self, world, kw=3, kp=100, mu=0.7, vmax=0.5, L=0.075):
    Control.__init__(self, world)

    self.g = 9.8
    self.kw = kw
    self.kp = kp
    self.mu = mu
    self.amax = self.mu * self.g
    self.vmax = vmax
    self.L = L

    self.lastth = 0
    self.ieth = 0
    self.iep = 0
    self.interval = Interval(filter=True, initial_dt=0.016)

    self.eth = 0

  @property
  def error(self):
    return self.eth

  def output(self, robot):
    if robot.field is None: return 0,0
    # Ângulo de referência
    th = robot.field.F(robot.pose)
    # Erro angular
    eth = angError(th, robot.th)
    # Tempo desde a última atuação
    dt = self.interval.getInterval()
    self.ieth = sat(self.ieth + eth*dt, 5)
    # Derivada da referência
    dth = filt(angError(th, self.lastth) / dt, 100)

    # Lei de controle da velocidade angular
    w = dth + self.kw * np.sign(eth) * np.sqrt(np.abs(eth)) #+ self.kw/100.0 * self.ieth 

    # Velocidade limite de deslizamento
    v1 = self.amax / np.abs(w) if w != 0 else math.inf

    # Velocidade limite das rodas
    v2 = self.vmax - self.L * np.abs(w) / 2

    # Velocidade limite de aproximação
    dTarget = norm(robot.pos, robot.field.Pb) if robot.pos[0] > -.6 else np.abs(robot.field.Pb[1] - robot.pos[1])
    e = (dTarget-0.015) ** 2
    self.iep = self.iep + dt*e if self.iep < 1.5 else 0

    v3 = self.kp * e + self.kp/80 * self.iep  + robot.vref if dTarget > 0.015 else 0

    # Velocidade linear é menor de todas
    v  = max(min(v1, v2, v3), 0)
    
    # Atualiza a última referência
    self.lastth = th
    robot.lastControlLinVel = v

    # Atualiza variáveis de estado
    self.eth = eth
    
    if robot.spin == 0: return (v * robot.direction, w)
    else: return (0, 60 * robot.spin)