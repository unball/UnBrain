import time
from tools.interval import Interval
from tools import adjustAngle, norml, derivative, angularDerivative, unit, angl, ang
from control.UFC import UFC_Simple
import numpy as np
import math

class EntriesVec:
    def __init__(self, past=20):
        self.past = 20
        self.vec = [0.0] * self.past

    def add(self, value):
        self.vec = [value] + self.vec[0:self.past-1]

    @property
    def value(self):
        return self.vec[0]

class Element:
    def __init__(self, world):
        self.world = world
        self.xvec = EntriesVec()
        self.yvec = EntriesVec()
        self.thvec_raw = EntriesVec()
        self.linvel = (0,0)
        self.angvel = 0
        self.interval = Interval(initial_dt=0.016)

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


    def raw_update(self, x=0, y=0, th=0):
        """Atualiza a posição do objeto, atualizando também o valor das posições anteriores."""
        self.dprev_x = self.prev_x
        self.dprev_y = self.prev_y
        self.prev_x = self.inst_x
        self.prev_y = self.inst_y
        self.prev_th = th
        self.inst_x = self.x
        self.inst_y = self.y
        self.xvec.add(self.world.field.side * x)
        self.yvec.add(y)
        self.thvec_raw.add(th)
    
        
    def update_element_FIRASim(self, x, y, vx, vy, w=0):
        self.xvec.add(self.world.field.side * x)
        self.yvec.add(y)
        self.linvel = (vx, vy)
        self.angvel = w
        self.interval.update()

    @property
    def x(self):
        return self.xvec.value

    @property
    def y(self):
        return self.yvec.value

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def vx_raw(self):
        return self.linvel[0]

    @property
    def vx(self):
        return self.vx_raw

    @property
    def vy_raw(self):
        return self.linvel[1]

    @property
    def vy(self):
        return self.vy_raw

    @property
    def v(self):
        return (self.vx, self.vy)

    @property
    def velmod(self):
        return norml(self.v)
    
    def calc_velocities(self, dt):
        """Estima a velocidade do objeto por meio do pose atual, pose anterior e o intervalo de tempo passado `dt`. A velocidade computada é suavizada por uma média exponencial: \\(v[k] = v_{\\text{estimado}} \\cdot \\alpha + v[k-1] \\cdot (1-\\alpha)\\) onde \\(v_{\\text{estimado}} = \\frac{r[k]-r[k-1]}{dt}\\)"""
    
        vx = (self.inst_x-self.prev_x) / dt
        vy = (self.inst_y-self.prev_y) / dt

        ax = (self.inst_x-2*self.prev_x+self.dprev_x) / dt**2
        ay = (self.inst_y-2*self.prev_y+self.dprev_y) / dt**2

        self.inst_vx = (vx + sum(self.vx_ant)) / 11.0
        self.inst_vy = (vy + sum(self.vy_ant)) / 11.0

        self.vx_ant = self.shift(vx, self.vx_ant)
        self.vy_ant = self.shift(vy, self.vy_ant)

        self.inst_ax = (ax + sum(self.ax_ant)) / 11.0
        self.inst_ay = (ay + sum(self.ay_ant)) / 11.0

        self.ax_ant = self.shift(ax, self.ax_ant)
        self.ay_ant = self.shift(ay, self.ay_ant)

        self.linvel = (vx, vy)

    def shift(self, data, array):
        return [data] + array[:-1]


class Robot(Element):
    def __init__(self, world, id):
        super().__init__(world)
        self.id = id

    def update(self, x, y, th):
        w = self.thvec_raw.add(th)
        super().update(x,y,w)
        
    def update_FIRASim(self, x, y, th, vx, vy, w):
        self.thvec_raw.add(th)
        super().update_element_FIRASim(x,y,vx,vy,w)

class TeamRobot(Robot):
    def __init__(self, world, id, control=None, on=False):
        super().__init__(world, id)

        self.field = None
        self.vref = math.inf
        self._on = on
        self.spin = 0
        self.spinTime = 0
        self.spinTimeOut = 0.5
        self.entity = None
        self.timeLastResponse = None
        self.lastControlLinVel = 0
        self.direction = 1
        
        self.spinTime = 0
        self.spinTimeOut = 0.05
        self.forcedAliveTime = 0
        self.forcedAliveTimeTimeOut = 0

    @property
    def on(self):
        return self._on

    def turnOff(self):
        self._on = False
        self.entity = None
        self.spin = 0

    def turnOn(self):
        self._on = True

    def updateField(self, field):
        self.field = field

    def stop(self):
        self.radio.send([(0,0) for robot in self.world.team])

    def updateEntity(self, entityClass, forced_update=False, **kwargs):
        newEntity = entityClass(self.world, self, **kwargs)
        if self.entity is None or self.entity.__class__.__name__ != entityClass.__name__ or not self.entity.equalsTo(newEntity) or forced_update:
            #print("mudou entidade do robô {0}: de {1} para {2}".format(self.id, self.entity.__class__.__name__, entityClass.__name__))
            if self.entity is not None: self.entity.onExit()
            self.entity = newEntity

    def isEntityLocked(self):
        if self.entity is None: return False
        else: return self.entity.isLocked()

    @property
    def thvec(self):
        # return [th+np.pi for th in self.thvec_raw.vec]
        return [th + (np.pi if self.direction == -1 else 0) for th in self.thvec_raw.vec]

    @property
    def th_raw(self):
        return self.thvec[0]

    @property
    def th(self):
        # return self.th_raw
        return self.th_raw if self.world.field.side == 1 else adjustAngle(np.pi - self.th_raw)

    @property
    def pose(self):
        return (self.x, self.y, self.th)

    @property
    def w_raw(self):
        return self.angvel

    @property
    def w(self):
        return self.world.field.side * self.w_raw
    
    @property
    def v_signed(self):
        direction = 1 if np.abs(ang(self.v, unit(self.th))) < np.pi/2 else -1
        return self.velmod * direction

    def setSpin(self, dir=1, timeOut=0.25):
        if self.spin != 0:
            return

        if dir != 0:
            self.spin = dir
        
        self.spinTime = time.time()
        self.spinTimeOut = timeOut

    def updateSpin(self):

        if time.time() - self.spinTime < self.spinTimeOut:
            self.spin = 0
    
    def isAlive(self):
        """Verifica se o robô está vivo baseado na relação entre a velocidade enviada pelo controle e a velocidade medida pela visão"""
        # if time.time() - self.forcedAliveTime < self.forcedAliveTimeTimeOut:
        #     return True

        if not self.on:
            self.timeLastResponse = time.time()
            return True

        ctrlVel = np.abs(self.lastControlLinVel)
        
        if ctrlVel < 0.01 or self.spin != 0:
            self.timeLastResponse = time.time()
            return True
        
        if self.velmod / ctrlVel < 0.1:
            if self.timeLastResponse is not None:
                dt = time.time() - self.timeLastResponse
                if dt is not None and dt > 0.33:
                    # self.keepAlive(3)
                    return False
        else:
            self.timeLastResponse = time.time()
        
        return True


    def keepAlive(self, timeToKeepAlive):
        self.forcedAliveTime = time.time()
        self.forcedAliveTimeTimeOut = timeToKeepAlive


class Ball(Element):
    def __init__(self, world):
        super().__init__(world)

    # def setSpin(self, dir=1, timeout=0.25):
    #     if dir != 0: 
    #         # Atualiza a direção do spin
    #         self.spin = dir

    #         # Atualiza o tempo de início do spin, se for um spin
    #         self.spinTime = time.time()

    #         # Diz o tempo de duração do spin
    #         self.spinTimeOut = timeout
    #     else:
    #         self.spin = 0