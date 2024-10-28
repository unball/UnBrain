from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from strategy.field.goalKeeper import GoalKeeperField
from strategy.field.attractive import AttractiveField
from strategy.movements import goalkeep, spinGoalKeeper, goToBall, goToGoal, howFrontBall, howPerpBall, blockBallElipse, mirrorPosition, spinDefender
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, angl, insideEllipse, angl, unit, projectLine
from tools.interval import Interval
from control.goalKeeper import GoalKeeperControl
from control.defender import DefenderControl
from control.UFC import UFC_Simple
from control.SecAttacker import SecAttackerControl
import numpy as np
import math
import time

class ControlTester(Entity):
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
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = np.array(self.world.field.goalPos)
        vr = np.array(self.robot.v)
        oneSpiralMargin = (self.world.marginPos[0]-0.15, self.world.marginPos[1])
        
        robotBallAngle = ang(rr, rb)
        
        self.robot.vref = 0

        #Quad 1: X = -0.375 Y = +0.430
        #Quad 2: X = +0.375 Y = +0.430
        #Quad 3: X = +0.375 Y = -0.430
        #Quad 4: X = -0.375 Y = -0.430

        #Andar para frente e para trás
        if self.x == 1:
            if not -0.370 > rr[0] > -0.390 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.380,0.430]), Pb=(-0.380,0.430, 0))
                
            else: self.x = 2
        if self.x == 2:
            if not +0.390 > rr[0] > +0.370 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[0.380,0.430]), Pb=(0.380,0.430, np.pi/2))
                
            else: self.x = 3
        if self.x == 3:
            if not +0.390 > rr[0] > +0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[0.380,-0.430]), Pb=(0.380,-0.430, 0))
                
            else: self.x = 4
        if self.x == 4:
            if not -0.390 < rr[0] < -0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.380,-0.430]), Pb=(-0.380,-0.430, np.pi/2))
                
            else: self.x = 5
        if self.x == 5:
            if not -0.370 > rr[0] > -0.390 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(-0.380,0.430,0))
                
            else: self.x = 6
        if self.x == 6:
            if not +0.390 > rr[0] > +0.370 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(0.380,0.430,np.pi/2))
                
            else: self.x = 7
        if self.x == 7:
            if not +0.390 > rr[0] > +0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(0.380,-0.430, 0))
                
            else: self.x = 8
        if self.x == 8:
            if not -0.390 < rr[0] < -0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(-0.380,-0.430, np.pi/2))
                
            else: self.x = 9
        if self.x == 9:
            if not -0.370 > rr[0] > -0.390 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = UVF(self.world, (-0.380,0.430, 0), robot= self.robot, direction=0) #AttractiveField(Pb=(-0.360,-0.380, np.pi)) 
                
            else: self.x = 10
        if self.x == 10:
            if not +0.390 > rr[0] > +0.370 or not 0.420 < rr[1] < 0.440: #Não chegou no lugar certo
                self.robot.field = UVF(self.world, (0.380,0.430, np.pi/2), robot= self.robot, direction=0) #AttractiveField(Pb=(-0.360,-0.380, np.pi))

            else: self.x = 11
        if self.x == 11:
            if not +0.390 > rr[0] > +0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = UVF(self.world, (0.380,-0.430, 0), robot= self.robot, direction=0)

            else: self.x = 12
        if self.x == 12:
            if not -0.390 < rr[0] < -0.370 or not -0.420 > rr[1] > -0.440: #Não chegou no lugar certo
                self.robot.field = UVF(self.world, (-0.380,-0.430, np.pi/2), robot= self.robot, direction=0)
            else: self.x = 1
        # if rr[0] == 0.375 and rr[1] == 0.430:
        #     self.robot.field = DirectionalField(np.pi, Pb=(0.375,-0.430,np.pi))
        # if rr[0] == 0.375 and rr[1] == -0.430:
        #     self.robot.field = DirectionalField(np.pi, Pb=(-0.375,-0.430,1,5*np.pi))
        # if rr[0] == -0.375 and rr[1] == -0.430 :
        #     self.robot.field = DirectionalField(np.pi, Pb=(-0.375, 0.430,np.pi))
        # else:
        #     self.robot.field = DirectionalField(ang(rr,[-0.375,0.43]), Pb=(-0.375,0.430,np.pi))
        
        # if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) + 0.10*self.robot.movState and (self.robot.movState == 1 or abs(howPerpBall(rb, rr, rg)) < 0.1) and abs(angError(robotBallAngle, rr[2])) < (20+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.22 + self.robot.movState*0.4:
        #     #if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) and abs(angError(robotBallAngle, rr[2])) < (30+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.25:
        #     if self.robot.movState == 0:
        #         self.robot.ref = (*(rr[:2] + 1000*unit(rr[2])), rr[2])
        #     pose, gammavels = goToGoal(rg, rr, vr)
        #     self.robot.vref = 999
        #     self.robot.gammavels = (0,0,0)
        #     self.robot.movState = 1
        #     Kr = None
        #     pose = self.robot.ref
        #     singleObstacle = False
        # # Se não, vai para a bola
        # else:
        #     # Vai para a bola saturada em -0.60m em x
        #     rbfiltered = np.array([rb[0] if rb[0] > -0.40 else -0.40, rb[1]])
        #     pose, gammavels = goToBall(rbfiltered, rg, vb, self.world.marginPos)
        #     self.robot.vref = 999
        #     self.robot.gammavels = gammavels
        #     self.robot.movState = 0
        #     Kr = 0.04
        #     singleObstacle = False

        
        # self.robot.field = UVFDefault(self.world, pose, rr, direction=0, Kr=Kr, singleObstacle=singleObstacle, Vr=vr)