from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from strategy.field.areaAvoidance.avoidanceField import AvoidanceField
from strategy.field.areaAvoidance.avoidCircle import AvoidCircle
from strategy.field.areaAvoidance.avoidRect import AvoidRect
from strategy.field.areaAvoidance.avoidEllipse import AvoidEllipse
from ..entity.attacker import Attacker
from strategy.movements import goToBall, intercept
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, insideEllipse, sat, sats, unit
from tools.interval import Interval
from control.UFC import UFC_Simple
import numpy as np
import math
import time

class Midfielder(Attacker):
    def __init__(self, world, robot,
                 midfielderOffset = 0.35
        ):

        Attacker.__init__(self, world, robot)
        
        # Params
        self.midfielderOffset = midfielderOffset

        # States
        self.followLine = False

        self._control = UFC_Simple(self.world, enableInjection=False)

    def directionDecider(self):
        rr = np.array(self.robot.pos)
        rb = np.array(self.world.ball.pos)
        if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if  time.time()-self.lastChat > .3 and (not self.followLine and abs(angError(ref_th, rob_th)) > 90 * np.pi / 180 or \
                   self.followLine and abs(angError(ref_th, rob_th)) >  90 * np.pi / 180):
                self.robot.direction *= -1
                self.lastChat = time.time()
            
            # Inverter a direção se o robô ficar preso em algo
            elif not self.robot.isAlive() and self.robot.spin == 0:
                if time.time()-self.lastChat > .3:
                    self.lastChat = time.time()
                    self.robot.direction *= -1
                # self.robot.setSpin(1 if rr[1] > rb[1] else -1, timeOut = 0.13)
    
    def fieldDecider(self):
        # Variáveis úteis
        rr = np.array(self.robot.pos)
        vr = np.array(self.robot.v)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = np.array(self.world.field.goalPos)
        rl = np.array(self.world.field.size) - np.array([0, 0.14])

        otherAttackers = [robot for robot in self.world.team if type(robot.entity) == Attacker]
        otherAttacker = otherAttackers[0]

        goal = [rg[0], 0.10 * np.sign(otherAttacker.y)]
        #print(goal)
        # Atualiza histórico de velocidade do robô
        self.vravg = 0.995 * self.vravg + 0.005 * norml(vr)

        # Define estado do movimento
        # Ir até a bola
        if self.attackState == 0:
            if otherAttacker.entity.attackState == 1: self.attackState = 0
            else:
                #if self.alignedToGoal(rb, rr, rg):
                if intercept(rr, rb, unit(self.robot.th), goal, vb, vrref=0.5) or self.alignedToGoal(rb, rr, rg):
                    self.attackState = 1
                    self.attackAngle = self.robot.th#ang(rr, goal)#self.angleToAttack(rr, rb, rg)
                    self.interceptTimeOver = time.time() + 1
                # elif self.alignedToBall(rb, rr):
                #     self.attackState = 2
                #     self.attackAngle = ang(rr, rb) # preciso melhorado
                else: self.attackState = 0

        # Ataque ao gol
        elif self.attackState == 1:
            #if self.alignedToGoalRelaxed(rb, rr, rg):
            if time.time() < self.interceptTimeOver or self.alignedToGoalRelaxed(rb, rr, rg):
                self.attackState = 1
            else:
                self.attackState = 0

        # Ataque à bola
        elif self.attackState == 2:
            if  self.alignedToBallRelaxed(rb, rr):
                self.attackState =  2
            else:
                self.attackState = 0

        # Movimento de alinhamento
        if self.attackState == 0:
            Pb = goToBall(rb, vb, rg, rr, rl, self.vravg, self.ballOffset)
            Pb = np.array([Pb[0]-self.midfielderOffset,Pb[1],Pb[2]])
            
            if len(otherAttackers) > 0:
                rro = np.array(otherAttacker.pos)

                if rro[0] > 0.4:
                    self.robot.vref = 0
                    self.robot.field = UVF((0.4, sat(rb[1], 0.35), np.pi/2 * np.sign(rb[1]-rr[1])), radius=self.spiralRadius)
                    #self.followLine = True
                    self.followLine = False

                else:
                    self.followLine = False
                
            else: self.followLine = False
            
            if not self.followLine:

                if rb[0] > 0.6:
                    self.robot.vref = 0
                    PmidFilder = [0.1, -0.15 * np.sign(otherAttacker.y)]
                    self.robot.field = UVF((*PmidFilder, ang(PmidFilder, goal)), radius=0.05)
                else:
                    Pb = goToBall(rb, vb, rg, rr, rl, self.vravg, self.ballOffset)
                    self.robot.field = UVF(Pb, radius=self.spiralRadius, Kr=0.3)

                # if np.abs(rb[1]) > rl[1]:
                #     self.robot.vref = math.inf
                #     self.robot.field = UVF(Pb, direction=-np.sign(rb[1]), radius=self.spiralRadiusCorners)
                # else:
                #     self.robot.vref = self.approximationSpeed
                #     self.robot.field = UVF(Pb, radius=self.spiralRadius)
        
        # Movimento reto
        elif self.attackState == 1 or self.attackState == 2:
            self.robot.vref = 1#sats(norml(vb), 0.5, math.inf)
            self.robot.field = DirectionalField(self.attackAngle, Pb=rr)

        # Campo para evitar área aliada
        a, b = self.world.field.areaEllipseSize
        center = self.world.field.areaEllipseCenter
        self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(center, 0.6*a, 0.80*b), borderSize=0.15)

        # Obtém outros aliados
        otherAllies = [robot for robot in self.world.team if robot != self.robot]
        enemies = [robot for robot in self.world.enemies]

        # Campo para evitar área inimiga
        if np.any([insideEllipse(robot.pos, a, b, rg) for robot in otherAllies]):
            self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(rg, 0.6*a, 0.80*b), borderSize=0.15)

        # Campo para evitar outro atacante
        if self.attackState == 0:
            for robot in [robot for robot in otherAllies if robot.entity.__class__ == Attacker]:
                self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.15), borderSize=0.20)

        # for robot in self.world.team:
        #     if robot.id != self.robot.id:
        #         if robot.entity.__class__.__name__ ==  "Attacker":
        #             if robot.entity.attackState != 0 and self.attackState == 0:
        #                 self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(rg, 0.6*a, 0.80*b), borderSize=0.15)
        #                 self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.05), borderSize=0.05)
        #             elif insideEllipse(robot.pos, a, b, rg):
        #             # elif norm(robot.pos, rb) < norm(rr, rb):
        #                 self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(rg, 0.6*a, 0.80*b), borderSize=0.15)
        #         else:
        #             self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.05), borderSize=0.05)


