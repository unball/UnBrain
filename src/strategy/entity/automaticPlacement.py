from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from tools import angError
from control.UFC import UFC_Simple
import numpy as np
import time

class AutomaticPlacement(Entity):
    def __init__(self, world, robot, automaticPose, side=1):
        super().__init__(world, robot)

        self._control = UFC_Simple(self.world)
        self.lastChat = 0
        self.goalPose = automaticPose
        self.spiralRadius = 0.07

        self.outOfPosition = False

    @property
    def control(self):
        return self._control
    
    def equalsTo(self):
        return True

    def onExit(self):
        pass
        
    def directionDecider(self):
       if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                self.robot.direction *= -1
                self.lastChat = time.time()

            # Inverter a direção se o robô ficar preso em algo
            elif not self.robot.isAlive() and self.robot.spin == 0:
                self.lastChat = time.time()
                self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pose)

        # robo fora da posição 
            # o que define robo fora da posição?
            # vai para posição UVF
        # robo na posição
            # corrige direção com campo direcional

        if( np.abs(self.goalPose[0] - 0.01) <= rr[0] <= np.abs(self.goalPose[0] + 0.01) ) and ( np.abs(self.goalPose[1] - 0.01) <= rr[1] <= np.abs(self.goalPose[1] + 0.01) ):
            self.robot.field = DirectionalField(self.goalPose[2])
        else:
            if np.abs(self.goalPose[1]) > 0:
                self.robot.field = UVF(self.goalPose, direction=-np.sign(self.goalPose[1]), radius=self.spiralRadius)
            else: 
                self.robot.field = UVF(self.goalPose, radius=self.spiralRadius)
