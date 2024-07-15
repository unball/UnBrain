from ..entity import Entity
from strategy.field.UVF import UVF
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, angl, insideEllipse, angl, unit, projectLine
from strategy.field.DirectionalField import DirectionalField
from tools import angError
from control.UFC import UFC_Simple
import numpy as np
import time

class AutomaticPlacement(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)

        self._control = UFC_Simple(self.world)
        self.lastChat = 0
        self.x = 1

    @property
    def control(self):
        return self._control
    
    def equalsTo(self, otherTester):
        return True

    def onExit(self):
        pass
        
    def directionDecider(self):
       if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if time.time()-self.lastChat > 0.5:
                if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()

            # Inverter a direção se o robô ficar preso em algo
            if not self.robot.isAlive() and self.robot.spin == 0:
                self.lastChat = time.time()
                self.robot.direction *= -1 

    def fieldDecider(self):
        rr = np.array(self.robot.pose)

        # robo fora da posição 
            # o que define robo fora da posição?
            # vai para posição UVF
        # robo na posição
            # corrige direção com campo direcional


        #posições: primeiro = [-0.7, 0.0]; segundo = [-0.5, 0.0]; terceiro = [-0.25, 0.0] 
        if self.robot.id == 0:
            if not -0.65 < rr[0] < -0.75 or not -0.05 < rr[1] < 0.05: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.7, 0.0]), Pb=(-0.7, 0.0 ,2 * np.pi))
                print(self.robot.id)
                return
            while self.x != 1:
                self.robot.field = DirectionalField((0), Pb=(0.0, 0.0 ,0.0))
                self.x = 2
        if self.robot.id == 1:
            if not -0.45 < rr[0] < -0.55 or not -0.05 < rr[1] < 0.05: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.5, 0.0]), Pb=(-0.5, 0.0 ,0))
                print(self.robot.id)
                return
        if self.robot.id == 2:
            if not -0.20 < rr[0] < -0.30 or not -0.05 < rr[1] < 0.05: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.25, 0.0]), Pb=(-0.25, 0.0 ,2 * np.pi))
                print(self.robot.id)
                return
