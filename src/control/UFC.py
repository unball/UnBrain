from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

PLOT_CONTROL = False
if PLOT_CONTROL:
  import matplotlib.pyplot as plt

def close_event():
  plt.close() 


class UFC_Simple(Control):
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
    self.vbias = 0.4

    self.sd_min = 1e-4
    self.sd_max = 0.5

    self.lastth = [0,0,0,0]
    self.lastdth = 0
    self.interval = Interval(filter=True, initial_dt=0.016)
    self.lastnorm = 0
    self.enableInjection = enableInjection
    self.lastwref = 0
    self.lastvref = 0
    self.integrateinjection = 0
    self.loadedInjection = 0
    self.lastPb = np.array([0,0])
    self.vPb = np.array([0,0])

    self.eth = 0
    self.plots = {"ref":[], "out": [], "eth":[], "vref": [], "v": [], "wref": [], "w": [], "sd": [], "injection": [], "dth": []}

  @property
  def error(self):
    return self.eth

  def abs_path_dth(self, initial_pose, error, field, step = 0.01, n = 10):
    pos = np.array(initial_pose[:2])
    thlist = np.array([])

    count = 0

    for i in range(n):
      th = field.F(pos)
      thlist = np.append(thlist, th)
      pos = pos + step * unit(th)
      count += 1

    aes = np.sum(np.abs(angError(thlist[1:], thlist[:-1]))) / n
  
    return aes + 0.05 * abs(error)

  def controlLine(self, x, xmax, xmin):
    return sats((xmax - x) / (xmax - xmin), 0, 1)


  def output(self, robot):
    if robot.field is None: return 0,0
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

    # v4 = self.kv / abs(eth) + self.vbias

    # Velocidade linear é menor de todas
    sd = self.abs_path_dth(robot.pose, eth, robot.field)
    #if robot.id == 0: print(sd)
    Pb = np.array(robot.field.Pb[:2])

    if self.enableInjection:
      currentnorm = norm(robot.pos, robot.field.Pb)
      #print(self.integrateinjection)
      # if self.integrateinjection > 10:
      #   injection = 0
      # else:
      #   injection = 0.0015 / (abs(currentnorm - self.lastnorm) + 1e-3)
      # self.integrateinjection = max(self.integrateinjection + injection - 0.5, 0)
      # if abs(currentnorm - self.lastnorm) < 0.001:
      #   self.loadedInjection = 0.90 * self.loadedInjection + 10 * 0.10
      # else:
      #   self.loadedInjection = 0.90 * self.loadedInjection
      #injection = 0.0010 / (abs(currentnorm - self.lastnorm) + 1e-3)
      #injection = 2 * norml(self.vPb) * (np.dot(self.vPb, unit(robot.field.Pb[2])) < 0) * 0.10 / norm(robot.pos, robot.field.Pb[:2])
      
      # Only apply injection near
      d = norm(robot.pos, robot.field.Pb[:2])
      r1 = 0.10
      r2 = 0.50
      eta = sats((r2 - d) / (r2 - r1), 0, 1)

      # Injection if ball runs in oposite direction
      if np.dot(self.vPb, unit(robot.field.Pb[2])) < 0:
        raw_injection = max(-np.dot(self.vPb, unit(robot.field.Pb[2])), 0)
      else:
        raw_injection = 0.5 * max(np.dot(self.vPb, unit(robot.field.Pb[2])), 0)

      injection = raw_injection * eta
    else:
      currentnorm = 0
      injection = 0

    v5 = self.vbias + (self.vmax-self.vbias) * self.controlLine(np.log(sd), np.log(self.sd_max), np.log(self.sd_min))
    v  = min(v5, v3) + sat(injection, 1)
    #print(vtarget)
    #v  = max(min(self.vbias + (self.vmax-self.vbias) * np.exp(-self.kapd * sd), v3), self.loadedInjection * vtarget)#max(min(v1, v2, v3, v4), 0)
    #ev = self.lastvref - robot.velmod
    #v = 1 * norm(robot.pos, robot.field.Pb) + 0.1 * ev + 0.2
    # v = 0.25#0.5*np.sin(2*time.time())+0.5
    # w = 0#2*np.sin(5*time.time())
    
    # Atualiza a última referência
    self.lastth = self.lastth[1:] + [th]
    self.lastnorm = currentnorm
    robot.lastControlLinVel = v

    # Atualiza variáveis de estado
    self.eth = eth
    self.lastdth = dth
    self.lastwref = w
    self.lastvref = v
    self.vPb = 0.90 * self.vPb + 0.10 * (Pb - self.lastPb) / dt
    self.lastPb = Pb

    if PLOT_CONTROL:
      self.plots["eth"].append(eth * 180 / np.pi)
      self.plots["ref"].append(th * 180 / np.pi)
      self.plots["out"].append(robot.th * 180 / np.pi)
      self.plots["vref"].append(abs(v))
      self.plots["wref"].append(w)
      self.plots["v"].append(robot.velmod)
      self.plots["w"].append(robot.w)
      self.plots["sd"].append(sd)
      self.plots["injection"].append(injection)
      self.plots["dth"].append(dth)

      if len(self.plots["eth"]) >= 300 and robot.id == 0:
        t = np.linspace(0, 300 * 0.016, 300)
        fig = plt.figure()
        #timer = fig.canvas.new_timer(interval = 5000) 
        #timer.add_callback(close_event)
        plt.subplot(7,1,1)
        plt.plot(t, self.plots["eth"], label='eth')
        plt.plot(t, np.zeros_like(t), '--')
        plt.legend()
        plt.subplot(7,1,2)
        plt.plot(t, self.plots["ref"], '--', label='th_ref')
        plt.plot(t, self.plots["out"], label='th')
        plt.legend()
        plt.subplot(7,1,3)
        plt.plot(t, self.plots["vref"], '--', label='vref')
        plt.plot(t, self.plots["v"], label='v')
        plt.legend()
        plt.subplot(7,1,4)
        plt.plot(t, self.plots["wref"], '--', label='wref')
        plt.plot(t, self.plots["w"], label='w')
        plt.legend()
        plt.subplot(7,1,5)
        plt.plot(t, self.plots["sd"], label='sd')
        plt.legend()
        plt.subplot(7,1,6)
        plt.plot(t, self.plots["injection"], label='injection')
        plt.legend()
        plt.subplot(7,1,7)
        plt.plot(t, self.plots["dth"], label='dth')
        plt.legend()
        #timer.start()
        robot.stop()
        plt.show()
        #timer.stop()
        for plot in self.plots.keys(): self.plots[plot] = []
    
    #return (0,0)
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