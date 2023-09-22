from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class MidfielderControl(Control):
  """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
  def __init__(self, world, kw=4, kp=20, mu=0.3, vmax=1.5, L=L, enableInjection=False):
    Control.__init__(self, world)

    self.g = 9.8
    self.kw = kw
    self.kp = kp
    self.mu = mu
    self.amax = self.mu * self.g
    self.vmax = vmax
    self.L = L
    self.kv = 10
    self.vbias = 0.2
    self.kapd = 3

    self.lastth = [0,0,0,0]
    self.lastdth = 0
    self.interval = Interval(filter=True, initial_dt=0.016)
    self.lastnorm = 0
    self.lastwref = 0
    self.lastvref = 0

    self.eth = 0

  @property
  def error(self):
    return self.epos

  def output(self, robot):
    if robot.field is None: return 0,0

    epos = norml(self.point2intercep - rb) - norml(self.point2intercep - rr)
    v = epos*k
    # Ângulo de referência
    #th = (time.time()/1) % (2*np.pi) - np.pi#np.pi/2 * np.sign(time.time() % 3 - 1.5)#robot.field.F(robot.pose)
    th = robot.field.F(robot.pose)
    # Erro angular
    eth = angError(th, robot.th)

    # Tempo desde a última atuação
    dt = 0.016#self.interval.getInterval()

    # Derivada da referência
    dth = filt(0.5 * (th - self.lastth[-1]) / dt + 0.2 * (th - self.lastth[-2]) / (2*dt) + 0.2 * (th - self.lastth[-3]) / (3*dt) + 0.1 * (th - self.lastth[-4]) / (4*dt), 10)
    #dth = filt((th - self.lastth) / dt, 10)

    # Erro de velocidade angular
    ew = self.lastwref - robot.w

    # Lei de controle da velocidade angular
    w = dth + self.kw * np.sqrt(abs(eth)) * np.sign(eth) #* (robot.velmod + 1)
    #w = self.kw * eth + 0.3 * ew

    # Velocidade limite de deslizamento
    v1 = self.amax / np.abs(w)

    # Velocidade limite das rodas
    v2 = self.vmax - self.L * np.abs(w) / 2

    # Velocidade limite de aproximação
    v3 = self.kp * norm(robot.pos, robot.field.Pb) ** 2 + robot.vref

    v4 = self.kv / abs(eth) + self.vbias

    # Velocidade linear é menor de todas
    # sd = self.abs_path_dth(robot.pose, eth, robot.field)
    
    currentnorm = 0
    
    # v  = min(self.vbias + (self.vmax-self.vbias) * np.exp(-self.kapd * sd), v3) 
    # v  = min(self.vbias + (self.vmax-self.vbias) * np.exp(-self.kapd * sd), v3) 

    # Atualiza a última referência
    self.lastth = self.lastth[1:] + [th]
    self.lastnorm = currentnorm
    robot.lastControlLinVel = v

    # Atualiza variáveis de estado
    self.epos = epos
    self.lastdth = dth
    self.lastwref = w
    self.lastvref = v
    
    if robot.spin == 0: return (v * robot.direction, w)
    else: return (0, 60 * robot.spin)

# class UFC():
#   """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
#   def __init__(self):
#     self.g = 9.8
#     self.kw = 5.5
#     self.kp = 10
#     self.mu = 0.7
#     self.amax = self.mu * self.g
#     self.vmax = 2
#     self.L = 0.075

#     self.lastth = 0
#     self.interval = Interval(filter=True, initial_dt=0.016)

#   def actuate(self, robot):
#     if robot.field is None: return 0,0
#     # Ângulo de referência
#     th = robot.field.F(robot.pose)
#     # Erro angular
#     eth = angError(th, robot.th)
#     # Tempo desde a última atuação
#     dt = self.interval.getInterval()
#     # Derivada da referência
#     dth = sat(angError(th, self.lastth) / dt, 15)
#     # Computa phi
#     phi = robot.field.phi(robot.pose)
#     # Computa gamma
#     gamma = robot.field.gamma(dth, robot.velmod, phi)
#     #print("eth: {:.4f}\tphi: {:.4f}\tth: {:.4f}\trth: {:.4f}\t".format(eth*180/np.pi, phi, th*180/np.pi, robot.th*180/np.pi))
    
#     # Computa omega
#     omega = self.kw * np.sign(eth) * np.sqrt(np.abs(eth)) + gamma

#     # Velocidade limite de deslizamento
#     if phi != 0: v1 = (-np.abs(omega) + np.sqrt(omega**2 + 4 * np.abs(phi) * self.amax)) / (2*np.abs(phi))
#     if phi == 0: v1 = self.amax / np.abs(omega)

#     # Velocidade limite das rodas
#     v2 = (2*self.vmax - self.L * np.abs(omega)) / (2 + self.L * np.abs(phi))

#     # Velocidade limite de aproximação
#     v3 = self.kp * norm(robot.pos, robot.field.Pb) ** 2 + robot.vref

#     # Velocidade linear é menor de todas
#     v  = max(min(v1, v2, v3), 0)

#     # Lei de controle da velocidade angular
#     w = v * phi + omega
    
#     # Atualiza a última referência
#     self.lastth = th
#     robot.lastControlLinVel = v
    
#     if robot.spin == 0: return speeds2motors(v * robot.direction, w)
#     else: return speeds2motors(0, 60 * robot.spin)