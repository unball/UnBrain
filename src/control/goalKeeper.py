from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class GoalKeeperControl(Control):
  """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
  def __init__(self, world, kw=5, kp=100, mu=0.07, vmax=2, L=0.075):
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

    # Derivada da referência
    dth = sat(angError(th, self.lastth) / dt, 15)

    # Computa phi
    phi = robot.field.phi(robot.pose)

    # Computa gamma
    gamma = robot.field.gamma(dth, robot.velmod, phi)

    # Computa omega
    omega = self.kw * np.sign(eth) * np.sqrt(np.abs(eth))

    # Velocidade limite de deslizamento
    if phi != 0: v1 = (-self.kw * np.sqrt(np.abs(eth))  + np.sqrt(self.kw**2 + 4 * np.abs(phi) * self.amax)) / (2*np.abs(phi))
    if phi == 0: v1 = self.amax / np.abs(omega)

    # Velocidade limite das rodas
    v2 = (2*self.vmax - self.L * self.kw * np.sqrt(np.abs(eth))) / (2 + self.L * np.abs(phi))

    # Velocidade limite de aproximação
    v3 = self.kp * norm(robot.pos, robot.field.Pb) ** 2 + robot.vref

    # Velocidade linear é menor de todas
    vels = np.array([v1,v2,v3])
    v  = max(min(v1, v2, v3), 0)

    # Lei de controle da velocidade angular
    w = v * phi + omega

    # Atualiza a última referência
    self.lastth = th
    robot.lastControlLinVel = v

    # Atualiza variáveis de estado
    self.eth = eth
    
    if robot.spin == 0: return (v * robot.direction, w)
    else: return (0, 60 * robot.spin)