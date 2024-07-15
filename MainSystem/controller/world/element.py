from controller.tools import angError, shift, angl, unit
import numpy as np


class Element(object):
  """Classe mãe que implementa um elemento de jogo como bola ou robô"""

  def __init__(self, world):
    self.world = world
    """Elemento deve ter uma referência ao mundo"""

    self.timeStep = 3
    """Número de intervalos de tempo do mundo que o dado da visão deve estar atrasado"""

    self.inst_x = 0
    """Posição x atual"""
    
    self.inst_y = 0
    """Posição y atual"""
    
    self.inst_th = 0
    """Ângulo atual"""

    self.prev_x = 0
    """Posição x anterior"""
    
    self.prev_y = 0
    """Posição y anterior"""
    
    self.prev_th = 0
    """Ângulo anterior"""

    self.dprev_x = 0
    """Posição x anterior anterior"""
    
    self.dprev_y = 0
    """Posição y anterior anterior"""

    self.inst_vx = 0
    """Estimativa da velocidade na direção x"""
    
    self.inst_vy = 0
    """Estimativa da velocidade na direção y"""
    
    self.inst_w = 0
    """Estimativa da velocidade angular"""
    
    self.vx_ant = [.0]*10
    """Valores das últimas 10 velocidades na direção x"""

    self.vy_ant = [.0]*10
    """Valores das últimas 10 velocidades na direção y"""

    self.inst_ax = 0
    """Estimativa da aceleração na direção x"""
    
    self.inst_ay = 0
    """Estimativa da aceleração na direção y"""
    
    self.ax_ant = [.0]*10
    """Valores das últimas 10 acelerações na direção x"""

    self.ay_ant = [.0]*10
    """Valores das últimas 10 acelerações na direção y"""
    
    self.poseDefined = False
    """Flag que indica se a pose já foi definida alguma vez via `update`"""
  
  def __repr__(self):
    """Representação formal do objeto. Retorna um pretty-printer dos atributos"""
    x = 'x: ' + str(self.inst_x) + '\n'
    y = 'y: ' + str(self.inst_y) + '\n'
    th = 'th: ' + str(self.inst_th) + '\n'
    vx = 'vx: ' + str(self.inst_vx) + '\n'
    vy = 'vy: ' + str(self.inst_vy) + '\n'
    w = 'w: ' + str(self.inst_w)
    info = x + y + th + vx + vy + w
    return info

  def update(self, x=0, y=0, th=0):
    self.raw_update(x, y, th)

  def raw_update(self, x=0, y=0, th=0):
    """Atualiza a posição do objeto, atualizando também o valor das posições anteriores."""
    self.dprev_x = self.prev_x
    self.dprev_y = self.prev_y
    self.prev_x = self.inst_x
    self.prev_y = self.inst_y
    self.prev_th = self.inst_th
    self.inst_x = x
    self.inst_y = y
    self.inst_th = th
    self.poseDefined = True


  @property
  def pos(self):
    """Retorna a posição \\([x,y]\\) do objeto como uma lista."""
    return [self.x, self.y]

  @property
  def raw_pos(self):
    """Retorna a posição \\([x,y]\\) do objeto como uma lista."""
    return [self.inst_x, self.inst_y]

  @property
  def pose(self):
    """Retorna a pose \\([x,y,\\theta]\\) do objeto um numpy array."""
    return np.array([self.x, self.y, self.th])

  @property
  def raw_pose(self):
    """Retorna a pose \\([x,y,\\theta]\\) do objeto um numpy array."""
    return np.array([self.inst_x, self.inst_y, self.inst_th])

  @property
  def th(self):
    """Retorna o ângulo do objeto"""
    return self.inst_th
    thVec = unit(self.inst_th)
    return angl((thVec[0] * self.world.fieldSide, thVec[1])) #+ self.timeStep * self.w * self.world.dt

  @property
  def raw_th(self):
    return self.inst_th

  @raw_th.setter
  def raw_th(self, th):
    """Atualiza direto a variável que contém o theta da visão"""
    self.inst_th = th

  def setTh(self, th):
    """Atualiza o ângulo do objeto diretamente (sem afetar o ângulo anterior)."""
    thVec = unit(th)
    self.inst_th = angl((-thVec[0], thVec[1]))

  @property
  def vel(self):
    """Retorna a velocidade do objeto no formato de lista: \\([v_x, v_y]\\)"""
    return [self.vx, self.vy]

  @property
  def raw_vel(self):
    return [self.inst_vx, self.inst_vy]

  @property
  def vx(self):
    return self.inst_vx

  @property
  def vy(self):
    return self.inst_vy

  @property
  def acc(self):
    """Retorna a aceleração do objeto no formato de lista: \\([a_x, a_y]\\)"""
    return [self.inst_ax, self.inst_ay]

  @property
  def raw_acc(self):
    return [self.inst_ax, self.inst_ay]

  @property
  def velmod(self):
    """Retorna o módulo da velocidade do objeto: \\(\\sqrt{v_x^2+v_y^2}\\)"""
    return np.sqrt(self.inst_vx**2+self.inst_vy**2)

  @property
  def accmod(self):
    """Retorna o módulo da aceleração do objeto: \\(\\sqrt{a_x^2+a_y^2}\\)"""
    return np.sqrt(self.inst_ax**2+self.inst_ay**2)

  @property
  def velang(self):
    """Retorna o ângulo do vetor velocidade do objeto: \\(\\text{arctan2}(v_y, v_x)\\)"""
    return np.arctan2(self.inst_vy, self.inst_vx)

  @property
  def raw_velang(self):
    return np.arctan2(self.inst_vy, self.inst_vx)

  @property
  def w(self):
    """Retorna a velocidade angular do objeto"""
    return self.inst_w
    return self.inst_w * self.world.fieldSide

  @property
  def raw_w(self):
    return self.inst_w

  @w.setter
  def w(self, w):
    """Atualiza a velocidade angular do objeto"""
    self.inst_w = w

  def calc_velocities(self, dt, alpha=0.5, thalpha=0.8, accalpha=0.2):
    """Estima a velocidade do objeto por meio do pose atual, pose anterior e o intervalo de tempo passado `dt`. A velocidade computada é suavizada por uma média exponencial: \\(v[k] = v_{\\text{estimado}} \\cdot \\alpha + v[k-1] \\cdot (1-\\alpha)\\) onde \\(v_{\\text{estimado}} = \\frac{r[k]-r[k-1]}{dt}\\)"""
    
    vx = (self.inst_x-self.prev_x) / dt
    vy = (self.inst_y-self.prev_y) / dt

    ax = (self.inst_x-2*self.prev_x+self.dprev_x) / dt**2
    ay = (self.inst_y-2*self.prev_y+self.dprev_y) / dt**2

    self.inst_vx = (vx + sum(self.vx_ant)) / 11.0
    self.inst_vy = (vy + sum(self.vy_ant)) / 11.0

    self.vx_ant = shift(vx, self.vx_ant)
    self.vy_ant = shift(vy, self.vy_ant)

    self.inst_ax = (ax + sum(self.ax_ant)) / 11.0
    self.inst_ay = (ay + sum(self.ay_ant)) / 11.0

    self.ax_ant = shift(ax, self.ax_ant)
    self.ay_ant = shift(ay, self.ay_ant)
    
    # newVelx = ((self.inst_x - self.prev_x)/dt)*alpha + (self.inst_vx)*(1-alpha)
    # newVely = ((self.inst_y - self.prev_y)/dt)*alpha + (self.inst_vy)*(1-alpha)

    # self.inst_ax = ((newVelx-self.inst_vx)/dt)*accalpha + (self.inst_ax)*(1-accalpha)
    # self.inst_ay = ((newVely-self.inst_vy)/dt)*accalpha + (self.inst_ay)*(1-accalpha)

    # self.inst_vx = newVelx
    # self.inst_vy = newVely

    self.inst_w = (angError(self.inst_th, self.prev_th)/dt)*thalpha + (self.inst_w)*(1-thalpha)

  @property
  def x(self):
    """Retorna a posição \\(x\\) atual do objeto"""
    return self.inst_x #+ self.timeStep * self.vx * self.world.dt

  @property
  def raw_x(self):
    return self.inst_x

  @property
  def y(self):
    """Retorna a posição \\(y\\) atual do objeto"""
    return self.inst_y #+ self.timeStep * self.vy * self.world.dt
    
  @property
  def raw_y(self):
    """Retorna a posição \\(y\\) atual do objeto"""
    return self.inst_y