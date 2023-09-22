from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from strategy.field.goalKeeper import GoalKeeperField
from strategy.field.attractive import AttractiveField
from strategy.movements import goalkeep, spinGoalKeeper
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, angl
from tools.interval import Interval
from control.goalKeeper import GoalKeeperControl
from control.UFC import UFC_Simple
import numpy as np
import math
import time

class GoalKeeper(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)

        self._control = GoalKeeperControl(world)
        self.lastChat = 0
        self.state = "Stable"

    @property
    def control(self):
        return self._control

    def equalsTo(self, otherGoalKeeper):
        return True

    def onExit(self):
        pass

    def setGoalKeeperControl(self):
        self._control = GoalKeeperControl(self.world)
    
    def setAttackerControl(self):
        self._control = UFC_Simple(self.world)
        
    def directionDecider(self):
       if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th
            # print('Rob_th:', rob_th)

            # if norm(self.robot.pos, self.world.ball.pos) < 0.02:
            #     self.robot.setSpin(np.sign(self.robot.y - self.world.ball.y), timeOut=0.1)
            # print('isAlive:')
            # print(self.robot.isAlive())

            if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180: #and time.time()-self.lastChat > .3:
                self.robot.direction *= -1
                self.lastChat = time.time()
            
            # Inverter a direção se o robô ficar preso em algo
            elif not self.robot.isAlive() and self.robot.spin == 0:
                if time.time()-self.lastChat > .3:
                    self.lastChat = time.time()
                    self.robot.direction *= -1
                    # self.robot.setSpin(np.sign(self.robot.y - self.world.ball.y), timeOut=0.1)

    def fieldDeciderMS(self):
        rr = np.array(self.robot.pos)
        thr = self.robot.pose[2]
        vr = np.array(self.robot.v)
        # self.vravg = 0.995 * self.vravg + 0.005 * norml(vr)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = -np.array(self.world.field.goalPos)
        rg[0] += 0.12
    
         # Aplica o movimento
        self.robot.vref = 0

        self.robot.setSpin(spinGoalKeeper(rb, rr, rg), timeOut = 0.1)
        
        self.setGoalKeeperControl()

        Pb = goalkeep(rb, vb, rr, rg)
        if np.abs(rr[0]-rg[0]) > 0.05:
            Pb = goalkeep(rb, vb, rr, rg)
            self.robot.field = UVF((rg[0], Pb[1], Pb[2]), radius=0.04)
            print("Instável")
        else:
            print("Estável")
            Pb = goalkeep(rb, vb, rr, (rr[0], rg[1]))
            self.robot.field = DirectionalField(Pb[2], Pb=(rr[0], Pb[1], Pb[2]))

    def fieldDecider(self):
        rr = np.array(self.robot.pos)
        thr = self.robot.pose[2]
        vr = np.array(self.robot.v)
        # self.vravg = 0.995 * self.vravg + 0.005 * norml(vr)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = -np.array(self.world.field.goalPos)
        rg[0] += 0.12
    
         # Aplica o movimento
        self.robot.vref = 0

        self.robot.setSpin(spinGoalKeeper(rb, rr, rg), timeOut = 0.1)

        Pb = goalkeep(rb, vb, rr, rg)
        # print(Pb)
        # print('isAlive:' , self.robot.isAlive())
        # print(f"angulo: {thr}")
        if self.state == "Stable":
            # if np.abs(rr[0]-rg[0]) > 0.05 or (np.abs(thr-1.5) > 2 or np.abs(thr-4.7) > 2):
            # self.setGoalKeeperControl()
            if np.abs(rr[0]-rg[0]) > 0.07:
                self.state = "Unstable"
        elif self.state == "Unstable":
            if rr[0] > 0:
                self.setAttackerControl()
                self.state = "Far"
                # SETAR INSTABILIDADE CASO O ROBO ESTEJA VIRADO E FRENTE PRO GOL
                
            # elif (np.abs(rr[0]-rg[0]) < 0.05) and (np.abs(thr-1.5) < 2 or np.abs(thr-4.7) < 2):
            elif (np.abs(rr[0]-rg[0]) < 0.04):
                # self.setGoalKeeperControl()
                self.state = "Stable"
        else:
            # if (np.abs(rr[0]-rg[0]) < 0.05) and (np.abs(thr-1.5) < 2 or np.abs(thr-4.7) < 2): 
            self.state = "Unstable"
            # self.setGoalKeeperControl()

            # if (np.abs(rr[0]-rg[0]) < 0.04):
            #     self.state = "Stable"
            #     self.setGoalKeeperControl()


        # self.robot.field = UVF(Pb, spiral=0.01)
        # self.robot.field = DirectionalField(Pb[2], Pb=Pb) if np.abs(rr[0]-Pb[0]) < 0.07 else UVF(Pb, spiral=0.01)
        # print('estado do goleiro: ' + self.state)
        if self.state == "Stable":
            self.robot.field = DirectionalField(Pb[2], Pb=(rr[0], Pb[1], Pb[2]))
        elif self.state == "Unstable":
            self.robot.field = UVF(Pb, radius=0.02)
            # self.robot.field = AttractiveField((Pb[0], rg[1], Pb[2]))
            # self.robot.field = UVF((rg[0], rg[1], Pb[2]), radius=0.04)

        elif self.state == "Far":
            self.robot.field = UVF(Pb, radius=0.04)
        #self.robot.field = DirectionalField(Pb[2], Pb=Pb)
