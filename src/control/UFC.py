from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class UFC_Simple(Control):
    """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
    def __init__(self, world, kw=4, kp=10, mu=0.95, vmax=1, L=L, enableInjection=False):
      Control.__init__(self, world)

      self.g = 9.8
      self.kw = kw
      self.kp = kp
      self.mu = mu
      self.amax = self.mu * self.g
      self.vmax = vmax
      self.L = L

      self.lastth = 0
      self.interval = Interval(filter=False, initial_dt=0.016)

    def output(self, robot):
      if robot.field is None: return 0,0

      # self.vmax = 2*self.world.manualControlSpeedV
      # self.kw = 2*self.world.manualControlSpeedW

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
      gamma = robot.field.gamma(robot.pose, robot.gammavels)

      # Computa omega
      omega = self.kw * np.sign(eth) * np.sqrt(np.abs(eth)) + gamma

      # Velocidade limite de deslizamento
      if phi != 0:
        v1 = (-np.abs(omega) + np.sqrt(omega**2 + 4 * np.abs(phi) * self.amax)) / (2*np.abs(phi))
      if phi == 0:
        v1 = self.amax / np.abs(omega)      

      # Velocidade limite das rodas
      v2 = (2*self.vmax - self.L * np.abs(omega)) / (2 + self.L * np.abs(phi))

      # Velocidade limite de aproximação
      v3 = self.kp * norm(robot.pose, robot.field.Pb) ** 2 + robot.vref

      # Velocidade linear é menor de todas
      v  = max(min(v1, v2, v3), 0)

      # Lei de controle da velocidade angular
      w = v * phi + omega

      # Considera resposta lenta
      #if tau != 0: w = (w - w0 * tau/dt * (1-np.exp(-dt/tau))) / (1-tau/dt * (1-np.exp(-dt/tau)))
      
      # Satura w caso ultrapasse a mudança máxima permitida
      #w  = lastspeed.w + sat(w-lastspeed.w, motorangaccelmax * r * interval / L)
      
      # Atualiza a última referência
      self.lastth = th
      robot.lastControlLinVel = v

      if robot.spin == 0: return (v * robot.direction, w)
      else: return (0, 60 * robot.spin)