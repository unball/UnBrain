from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from strategy.field.goalKeeper import GoalKeeperField
from strategy.field.ellipse import DefenderField
from strategy.movements import goalkeep, blockBallElipse, spinGoalKeeper
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm
from tools.interval import Interval
from control.UFC import UFC_Simple
from control.defender import DefenderControl
from client.gui import clientProvider
import numpy as np
import math

class Defender(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)

        self._control = DefenderControl(self.world)
    @property
    def control(self):
        return self._control

    def equalsTo(self, otherDefender):
        return True

    def onExit(self):
        clientProvider().removeEllipse(self.robot.id)
        
    def directionDecider(self):
       if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th
            # print('Rob_th:', rob_th)

            if abs(angError(ref_th, rob_th)) > 120 * np.pi / 180:
                self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pos)
        vr = np.array(self.robot.v)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = -np.array(self.world.field.goalPos)

        # Executa spin se estiver morto
        if not self.robot.isAlive():
            self.robot.setSpin(-np.sign(rr[0]) if rr[1] > 0 else np.sign(rr[0]))
            return
        
         # Aplica o movimento
        self.robot.vref = 0

        if norm(rr, rg) < norm(rb, rg):
            self.robot.setSpin(spinGoalKeeper(rb, rr, rg), timeOut = 0.13)

        if np.sign(rb[1]) > 0 and rb[1] > rr[1] and rb[0] < -0.60 and rr[1] > 0.25 and np.abs(rr[0]-rb[0]) < 0.07:
            pose = (rr[0], rb[1], np.pi/2)
            self.robot.field = GoalKeeperField(pose, rb[0])
            self.robot.vref = 999
        elif np.sign(rb[1]) < 0 and rb[1] < rr[1] and rb[0] < -0.60 and rr[1] < -0.25 and np.abs(rr[0]-rb[0]) < 0.07:
            pose = (rr[0], rb[1], -np.pi/2)
            self.robot.field = GoalKeeperField(pose, rb[0])
            self.robot.vref = 999
        else:
            pose, spin = blockBallElipse(rb, vb, rr, self.world.field.areaEllipseCenter, *self.world.field.areaEllipseSize)
            self.robot.setSpin(spin)

            self.robot.vref = 0
            self.robot.field = DefenderField(pose, *self.world.field.areaEllipseSize, self.world.field.areaEllipseCenter)

        rm = self.world.field.areaEllipseCenter
        clientProvider().drawEllipse(self.robot.id, rm[0], rm[1], *self.world.field.areaEllipseSize, -np.pi/2, np.pi/2, None, False)
        # Pb = blockBallElipse(rb, vb, rr, rg) 
        # self.robot.field = DefenderField(Pb)
        