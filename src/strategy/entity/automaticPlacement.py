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

        if(rr[0] > self.goalPose[0] or rr[1] > self.goalPose[1]):
            self.robot.field = UVF(self.goalPose, radius=self.spiralRadius, Kr=0.03)

        self.robot.field = DirectionalField(self.goalPose[2])