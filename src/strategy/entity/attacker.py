from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from strategy.field.attractive import AttractiveField
from strategy.field.areaAvoidance.avoidanceField import AvoidanceField
from strategy.field.areaAvoidance.avoidCircle import AvoidCircle
from strategy.field.areaAvoidance.avoidRect import AvoidRect
from strategy.field.areaAvoidance.avoidEllipse import AvoidEllipse
from strategy.movements import goToBall, goToGoal, howFrontBall, howPerpBall, goalkeep, blockBallElipse, mirrorPosition, spinDefender, spinGoalKeeper
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, insideEllipse, angl, unit, projectLine
from tools.interval import Interval
from control.UFC import UFC_Simple
from control.goalKeeper import GoalKeeperControl
from client.gui import clientProvider
import numpy as np
import math
import time

class Attacker(Entity):
    def __init__(self, world, robot, 
                 perpBallLimiarTrackState = 0.075 * 0.20, 
                 perpBallLimiarAtackState = 0.075 * 2, 
                 alignmentAngleTrackState = 30, 
                 alignmentAngleAtackState = 90, 
                 spiralRadius = 0.07, 
                 spiralRadiusCorners = 0.05, 
                 approximationSpeed = 0.8, 
                 ballOffset = -0.03,
                 ballShift = 0,
                 slave = False
        ):

        Entity.__init__(self, world, robot)
        
        # Params
        self.perpBallLimiarTrackState = perpBallLimiarTrackState
        self.perpBallLimiarAtackState = perpBallLimiarAtackState
        self.alignmentAngleTrackState = alignmentAngleTrackState
        self.alignmentAngleAtackState = alignmentAngleAtackState
        self.spiralRadius = spiralRadius
        self.spiralRadiusCorners = spiralRadiusCorners
        self.approximationSpeed = approximationSpeed
        self.ballOffset = ballOffset
        self.ballShift = ballShift
        self.slave = slave
        self.elapsed = 0

        # States
        self.lastDirectionChange = 0
        self.attackAngle = None
        self.attackState = 0
        self.vravg = 0
        
        
        self.lastChat = 0

        self._control = UFC_Simple(self.world)
    @property
    def control(self):
        return self._control

    def equalsTo(self, otherAttacker):
        return self.slave == otherAttacker.slave

    def onExit(self):
        clientProvider().removeTarget(self.robot.id)
        clientProvider().removeLine(self.robot.id)

    def isLocked(self):
        return self.attackState == 1 or self.attackState == 2

    def directionDecider(self):
        if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if time.time()-self.lastChat > 0.5:
                if abs(angError(ref_th, rob_th)) > 120 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()
                
                # Inverter a direção se o robô ficar preso em algo
                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1

                    
    
    def inAttackRegion(self, rb, rr, rg, yrange=0.25, xgoal=0.75):
        return np.abs(rr[1] + (xgoal - rr[0]) / (rb[0] - rr[0]) * (rb[1] - rr[1])) < yrange

    def alignedToGoal(self, rb, rr, rg):
        return self.inAttackRegion(rb + 0.10 * angl(rg-rb), rr, rg) and howFrontBall(rb, rr, rg) < 0 and abs(angError(self.robot.th, ang(rb, rg))) < self.alignmentAngleTrackState * np.pi / 180

    def alignedToGoalRelaxed(self, rb, rr, rg):
        return howFrontBall(rb, rr, rg) < 0.10 #and abs(angError(self.robot.th, ang(rb, rg))) < self.alignmentAngleAtackState * np.pi / 180

    def fieldDecider(self):
        # Variáveis úteis
        rr = np.array(self.robot.pose)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = np.array(self.world.field.goalPos)
        vr = np.array(self.robot.v)
        oneSpiralMargin = (self.world.marginPos[0] - 0.1, self.world.marginPos[1] - 0.2)

        self.robot.vref = 0


        # Ângulo do robô até a bola
        robotBallAngle = ang(rr, rb)

        # Se estiver atrás da bola, estiver em uma faixa de distância "perpendicular" da bola, estiver com ângulo para o gol com erro menor que 30º vai para o gol
        #if howFrontBall(rb, rr, rg) < -0.03*(1-self.movState) and abs(howPerpBall(rb, rr, rg)) < 0.045 + self.movState*0.1 and abs(angError(ballGoalAngle, rr[2])) < (30+self.movState*60)*np.pi/180:
        if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) + 0.10*self.robot.movState and (self.robot.movState == 1 or abs(howPerpBall(rb, rr, rg)) < 0.1) and abs(angError(robotBallAngle, rr[2])) < (20+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.22 + self.robot.movState*0.4:
            #if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) and abs(angError(robotBallAngle, rr[2])) < (30+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.25:
            if self.robot.movState == 0:
                self.robot.ref = (*(rr[:2] + 1000*unit(rr[2])), rr[2])
            pose, gammavels = goToGoal(rg, rr, vr)
            self.robot.gammavels = (0,0,0)
            self.robot.movState = 1
            self.robot.vref = 999
            Kr = 0.03
            pose = self.robot.ref
        # Se não, vai para a bola
        else:
            # Vai para a bola saturada em -0.60m em x
            # rbfiltered = np.array([rb[0] if rb[0] > -0.40 else -0.40, rb[1]])
            pose, gammavels = goToBall(rb, rg, vb, self.world.marginPos)
            self.robot.vref = 0
            self.robot.gammavels = gammavels
            self.robot.movState = 0
            Kr = 0.04#self.auxRobot is not None and type(self.auxRobot.entity) == Defender
        
        # Decide quais espirais estarão no campo e compõe o campo
        #if abs(rb[0]) > self.world.xmaxmargin: self.world.goalpos = (-self.world.goalpos[0], self.world.goalpos[1])

        # Muda o campo no gol caso a bola esteja lá
        if self.world.ball.x < -0.3:
            self.robot.vref = 0
            self.robot.field = AttractiveField(Pb=(-0.25,0,0))

        elif any(np.abs(rb) > oneSpiralMargin) and np.abs(rb[1]) >= 0.3:
            angle = -np.sign(rb[1]) / (1 + np.exp(-(rb[0]-oneSpiralMargin[0]) / 0.03)) * np.pi/2
            self.robot.gammavels = (0,0,0)
            self.robot.field = UVF(world=self.world, robot=self.robot, Pb=(*pose[:2], angle), direction=-np.sign(rb[1]))
        else: 
            #if howFrontBall(rb, rr, rg) > 0: radius = 0
            #else: radius = None
            self.robot.field = UVF(world=self.world, robot=self.robot, Pb=pose, direction=0)








        # # Obtém outros aliados
        # otherAllies = [robot for robot in self.world.team if robot != self.robot]
        # enemies = [robot for robot in self.world.enemies]

        # # Atualiza histórico de velocidade do robô
        # self.vravg = 0.995 * self.vravg + 0.005 * np.dot(vr, unit(ang(rr, rb)))
        
        # Pb = goToBall(rb, vb, rg, rr, rl, self.vravg, self.ballOffset - self.ballShift)
        
        # # if self.attackState == 0 and norm(rr, rb) < 0.085 and np.any([norm(rr, x.pos) < 0.20 for x in enemies]) and rr[0] > 0:
        # #     self.robot.setSpin(-np.sign(rr[1]), timeOut=1)
        # # else:
        # #     self.robot.setSpin(0)

        # if norm(rr, rb) < 0.085 and np.abs(rb[1]) > rl[1] and np.any([norm(rr, x.pos) < 0.20 for x in enemies]):
        #     self.robot.setSpin(-np.sign(rr[1]), timeOut=1)
        # else:
        #     self.robot.setSpin(0)

        # # Define estado do movimento
        # # Ir até a bola
        # if self.attackState == 0:
        #     if self.alignedToGoal(Pb[:2], rr, rg):
        #         self.attackState = 1
        #         #print("atacando")
        #         #self.attackAngle = self.angleToAttack(rr, rb, rg)
        #         self.attackAngle = ang(rr, rg)
        #         self.elapsed = time.time()

        #         clientProvider().drawLine(self.robot.id, rr[0], rr[1], rg[0], rg[1])
        #     # elif self.alignedToBall2(rb, rr):
        #     #     self.attackState = 2
        #     #     self.attackAngle =  self.robot.th if np.dot(unit(self.robot.th), rb- rr[:2]) > 0 else self.robot.th+np.pi #ang(rr, rb) # preciso melhorado
        #     #     self.elapsed = time.time()
        #     else: self.attackState = 0

        # # Ataque ao gol
        # elif self.attackState == 1:
        #     if self.alignedToGoalRelaxed(Pb[:2], rr, rg) :
        #         self.attackState =  1
        #     else:
        #         #print("indo até a bola")
        #         self.attackState = 0

        #         clientProvider().removeLine(self.robot.id)

        # # # Ataque à bola
        # # elif self.attackState == 2:
        # #     if  self.alignedToBallRelaxed2(rb, rr):
        # #         self.attackState =  2
        # #     else:
        # #         self.attackState = 0

        # # Movimento de alinhamento
        # if self.attackState == 0 or time.time()-self.elapsed < .2:

        #     if np.abs(Pb[1]) > rl[1]:
        #         self.robot.vref = math.inf
        #         self.robot.field = UVF(Pb, direction=-np.sign(rb[1]), radius=self.spiralRadiusCorners)

        #         clientProvider().drawTarget(self.robot.id, Pb[0], Pb[1], Pb[2])
        #     else:
        #         #rps = np.array([r.pos for r in enemies+otherAllies])
        #         # Pbv = avoidObstacle(Pb, rr[:2], rl-[0.15,0], rps)
        #         Pbv = Pb

        #         self.robot.vref = self.approximationSpeed + 2 * norml(vb)
        #         self.robot.field = UVF(Pbv, radius=self.spiralRadius, Kr=0.03)

        #         clientProvider().drawTarget(self.robot.id, Pbv[0], Pbv[1], Pbv[2])

        # # Movimento reto
        # elif self.attackState == 1 or self.attackState == 2:
        #     drb = norm(rr, rb)
        #     drg = norm(rr, rg)
        #     angle = (drg * ang(rr, rg) + drb * ang(rr, rb)) / (drb + drg)
        #     self.robot.vref = math.inf
        #     self.robot.field = DirectionalField(angle)

        #     clientProvider().drawTarget(self.robot.id, rg[0], rg[1], angle)
        
        #if self.attackState==0: self.elapsed = math.inf

        # # Campo para evitar área aliada
        # a, b = self.world.field.areaEllipseSize
        # center = self.world.field.areaEllipseCenter
        # self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(center, 0.6*a, 0.80*b), borderSize=0.15)

        # # Campo para evitar área inimiga
        # if np.any([insideEllipse(robot.pos, a, b, rg) for robot in otherAllies]):
        #     self.robot.field = AvoidanceField(self.robot.field, AvoidEllipse(rg, 0.6*a, 0.80*b), borderSize=0.15)
        
        # if self.attackState == 0 and rr[0] > 0 and norm(rr, rb) > 0.10:
        #    for robot in enemies:#otherAllies + enemies:
        #        if np.abs(ang(unit(angl(robot.pos-rr)), unit(self.robot.th))) < 30 * np.pi / 180:
        #         self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.08), borderSize=0.20)

        # if self.slave and self.attackState == 0:
        #     print("I {0} am slave".format(self.robot.id))
        #     for robot in [r for r in otherAllies if r.entity.__class__.__name__ ==  "Attacker"]:
        #         self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.08), borderSize=0.20)


        # Campo para evitar outro robô, (só se não estiver alinhado)
        #if self.attackState == 0:
        #    for robot in otherAllies + enemies:
        #        self.robot.field = AvoidanceField(self.robot.field, AvoidCircle(robot.pos, 0.08), borderSize=0.20)

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


