from abc import ABC, abstractmethod
from controller.strategy.movements import goToBall, goToGoal, projectBall, howFrontBall, howPerpBall, goalkeep, blockBallElipse, mirrorPosition, spinDefender, spinGoalKeeper
from controller.strategy.field import UVFDefault, GoalKeeperField, DefenderField, UVFavoidGoalArea
from controller.tools import ang, angError, norm, unit, projectLine
import numpy as np
import time

class Entity(ABC):
    def __init__(self, robot, color):
        super().__init__()

        self.robot = robot
        """Robô associado a esta entidade"""

        self.color = color
        self.mu = .07

    def directionDecider(self):
        """Altera a propriedade `dir` do robo de acordo com a decisão"""
        # Inverte se o último erro angular foi maior que 160º
        if abs(self.robot.lastAngError) > 120 * np.pi / 180:
            self.robot.dir *= -1

    @abstractmethod
    def movementDecider(self):
        """Altera a propriedade `field` do robo de acordo com a decisão"""
        pass

    @property
    def name(self):
        return self.__class__.__name__

class Attacker(Entity):
    def __init__(self, world, robot):
        super().__init__(robot, (0,0,255))

        self.world = world
        self.rg = (0,0)
        self.mu = .12
        self.auxRobot = None

    def setAuxRobot(self, auxRobot):
        self.auxRobot = auxRobot

    def movementDecider(self):
        # Dados necessários para a decisão
        if self.auxRobot is not None:
            ra = np.array(self.auxRobot.pose.copy())
            va = np.array(self.auxRobot.lastControlLinVel * unit(self.auxRobot.th))
        else:
            ra = None
            va = None
        rb = np.array(self.world.ball.pos.copy())
        vb = np.array(self.world.ball.vel.copy())
        ab = np.array(self.world.ball.acc.copy())
        rr = np.array(self.robot.pose)
        # if self.movState == 0:
        #     self.rg = np.array(self.world.goalpos) + [0,0.15 / (np.pi/2) * np.arctan(rb[1] / 0.1)]
        # else:
        #     rg = self.rg
        # rg = self.rg
        rg = np.array(self.world.goalpos)
        vr = np.array(self.robot.lastControlLinVel * unit(self.robot.th))
        oneSpiralMargin = (self.world.marginLimits[0]-0.15, self.world.marginLimits[1])

        # Executa spin se estiver morto
        if not self.robot.isAlive():
            self.robot.setSpin(-np.sign(rr[0]) if rr[1] > 0 else np.sign(rr[0]))
            return

        # Bola projetada com offset
        rbpo = projectBall(rb, vb, rr, rg, self.world.marginLimits)

        # Ângulo da bola até o gol
        ballGoalAngle = ang(rb, rg)

        # Ângulo do robô até a bola
        robotBallAngle = ang(rr, rb)

        # Se estiver atrás da bola, estiver em uma faixa de distância "perpendicular" da bola, estiver com ângulo para o gol com erro menor que 30º vai para o gol
        #if howFrontBall(rb, rr, rg) < -0.03*(1-self.movState) and abs(howPerpBall(rb, rr, rg)) < 0.045 + self.movState*0.1 and abs(angError(ballGoalAngle, rr[2])) < (30+self.movState*60)*np.pi/180:
        if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) + 0.10*self.robot.movState and (self.robot.movState == 1 or abs(howPerpBall(rb, rr, rg)) < 0.1) and abs(angError(robotBallAngle, rr[2])) < (20+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.22 + self.robot.movState*0.4:
            #if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) and abs(angError(robotBallAngle, rr[2])) < (30+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.25:
            if self.robot.movState == 0:
                self.robot.ref = (*(rr[:2] + 1000*unit(rr[2])), rr[2])
            pose, gammavels = goToGoal(rg, rr, vr)
            self.robot.vref = 999
            self.robot.gammavels = (0,0,0)
            self.robot.movState = 1
            Kr = None
            pose = self.robot.ref
            singleObstacle = False
        # Se não, vai para a bola
        else:
            # Vai para a bola saturada em -0.60m em x
            rbfiltered = np.array([rb[0] if rb[0] > -0.40 else -0.40, rb[1]])
            pose, gammavels = goToBall(rbfiltered, rg, vb, self.world.marginLimits)
            self.robot.vref = 999
            self.robot.gammavels = gammavels
            self.robot.movState = 0
            Kr = 0.04
            singleObstacle = False#self.auxRobot is not None and type(self.auxRobot.entity) == Defender
        
        # Decide quais espirais estarão no campo e compõe o campo
        #if abs(rb[0]) > self.world.xmaxmargin: self.world.goalpos = (-self.world.goalpos[0], self.world.goalpos[1])

        # Muda o campo no gol caso a bola esteja lá
        if self.world.ball.insideGoalArea():
            self.robot.vref = 0
            self.robot.field = UVFDefault(self.world, pose, rr, direction=-np.sign(rb[1]), radius=0, Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va)

        if any(np.abs(rb) > oneSpiralMargin) and not (np.abs(rb[1]) < 0.3):
            angle = -np.sign(rb[1]) / (1 + np.exp(-(rb[0]-oneSpiralMargin[0]) / 0.03)) * np.pi/2
            self.robot.gammavels = (0,0,0)
            self.robot.field = UVFDefault(self.world, (*pose[:2], angle), rr, direction=-np.sign(rb[1]), Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va, radius=0.07)
        else: 
            #if howFrontBall(rb, rr, rg) > 0: radius = 0
            #else: radius = None
            self.robot.field = UVFDefault(self.world, pose, rr, direction=0, Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va)

class Defender(Entity):
    def __init__(self, world, robot):
        super().__init__(robot, (0,255,0))

        self.world = world
    
    def directionDecider(self):
        """Altera a propriedade 'dir' do robô de acordo com a decisão"""
        # Inverte se o último erro angular foi maior que 90º
        if abs(self.robot.lastAngError) > 90 * np.pi / 180:
            self.robot.dir *= -1

    def movementDecider(self):
        # Dados necessários para a decisão
        rb = np.array(self.world.ball.pos.copy())
        vb = np.array(self.world.ball.vel.copy())
        rr = np.array(self.robot.pose)
        rg = np.array(self.world.rg)

        # Executa spin se estiver morto
        if not self.robot.isAlive() and norm(rb, rr) > 0.12:
            self.robot.setSpin()
            return
        
        if np.sign(rb[1]) > 0 and rb[1] > rr[1] and rb[0] < -0.60 and rr[1] > 0.25 and np.abs(rr[0]-rb[0]) < 0.07:
            pose = (rr[0], rb[1], np.pi/2)
            self.robot.field = GoalKeeperField(pose, rb[0])
            self.robot.gammavels = (0,0,0)
            self.robot.vref = 999
        elif np.sign(rb[1]) < 0 and rb[1] < rr[1] and rb[0] < -0.60 and rr[1] < -0.25 and np.abs(rr[0]-rb[0]) < 0.07:
            pose = (rr[0], rb[1], -np.pi/2)
            self.robot.field = GoalKeeperField(pose, rb[0])
            self.robot.gammavels = (0,0,0)
            self.robot.vref = 999
        else:
            pose, spin = blockBallElipse(rb, vb, rr, rg)
            self.robot.setSpin(spin, timeout = 0.1)

            self.robot.vref = 0
            self.robot.gammavels = (0,0,0)
            #self.robot.field = UVFavoidGoalArea(self.world, pose, rr)
            #self.robot.field = UVFDefault(self.world, pose, rr, direction = 0, spiral = False)

            self.robot.field = DefenderField(pose)

class GoalKeeper(Entity):
    def __init__(self, world, robot):
        super().__init__(robot, (255,0,0))

        self.world = world

    def directionDecider(self):
        """Altera a propriedade `dir` do robo de acordo com a decisão"""
        # Inverte se o último erro angular foi maior que 160º
        if abs(self.robot.lastAngError) > 90 * np.pi / 180:
            self.robot.dir *= -1

    def movementDecider(self):
        # Dados necessários para a decisão
        rb = np.array(self.world.ball.pos.copy())
        vb = np.array(self.world.ball.vel.copy())
        rr = np.array(self.robot.pose)
        rg = (np.array(self.world.rg) + [self.robot.size / 2, 0])

        
        self.robot.gammavels = (0,0,0)
        self.robot.vref = 0

        self.robot.setSpin(spinGoalKeeper(rb, rr, rg), timeout = 0.1)
        
        if np.abs(rr[0]-rg[0]) > 0.12:
            pose = goalkeep(rb, vb, rr, rg)
            self.robot.field = UVFDefault(self.world, pose, rr, direction=0, spiral=False)
        else: 
            pose = goalkeep(rb, vb, rr, (rr[0], rg[1]))
            self.robot.field = GoalKeeperField(pose, rg[0])
        #self.robot.field = UVFDefault(self.world, (rr[0], *pose[1:3]), rr, direction=0, spiral=False)
        #else: self.robot.field = GoalKeeperField((rr[0], *pose[1:3]))
        #self.robot.field = UVFDefault(self.world, pose, direction=0, radius=0.14)

class MidFielder(Entity):
    def __init__(self, world, robot, attackerRobot):
        super().__init__(robot, (255,255,0))
        
        self.attacker = attackerRobot
        self.world = world
        self.movState = 0
        self.mu = 0.07

    def movementDecider(self):
        # Dados necessários para a decisão
        ra = np.array(self.attacker.pose.copy())
        va = np.array(self.attacker.lastControlLinVel * unit(self.attacker.th))
        rb = np.array(self.world.ball.pos.copy())
        vb = np.array(self.world.ball.vel.copy())
        ab = np.array(self.world.ball.acc.copy())
        rr = np.array(self.robot.pose)
        # if self.movState == 0:
        #     self.rg = np.array(self.world.goalpos) + [0,0.15 / (np.pi/2) * np.arctan(rb[1] / 0.1)]
        # else:
        #     rg = self.rg
        # rg = self.rg
        rg = np.array(self.world.goalpos)
        vr = np.array(self.robot.lastControlLinVel * unit(self.robot.th))

        # Executa spin se estiver morto
        if not self.robot.isAlive():
            self.robot.setSpin(-np.sign(rr[0]) if rr[1] > rb[1] else np.sign(rr[0]))
            return

        # Bola projetada com offset
        rbpo = projectBall(rb, vb, rr, rg, self.world.marginLimits)

        # Ângulo da bola até o gol
        ballGoalAngle = ang(rb, rg)

        # Ângulo do robô até a bola
        robotBallAngle = ang(rr, rb)

        #if howFrontBall(rb, rr, rg) < -0.03*(1-self.movState) and abs(howPerpBall(rb, rr, rg)) < 0.045 + self.movState*0.1 and abs(angError(ballGoalAngle, rr[2])) < (30+self.movState*60)*np.pi/180:
        if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) + 0.10*self.robot.movState and (self.robot.movState == 1 or abs(howPerpBall(rb, rr, rg)) < 0.1) and abs(angError(robotBallAngle, rr[2])) < (20+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.22 + self.robot.movState*0.4:
            #if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) and abs(angError(robotBallAngle, rr[2])) < (30+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.25:
            if self.robot.movState == 0:
                self.robot.ref = (*(rr[:2] + 1000*unit(rr[2])), rr[2])
            pose, gammavels = goToGoal(rg, rr, vr)
            self.robot.vref = 999
            self.robot.gammavels = (0,0,0)
            self.robot.movState = 1
            Kr = None
            pose = self.robot.ref
            singleObstacle = False
        # Se não, vai para a bola
        else:
            rbfiltered = np.array([rb[0] if rb[0] > -0.40 else -0.40, rb[1]])
            pose, gammavels = goToBall(rbfiltered, rg, vb, self.world.marginLimits)
            self.robot.vref = 999
            self.robot.gammavels = gammavels
            self.robot.movState = 0
            Kr = 0.04
            singleObstacle = True
        
        # Decide quais espirais estarão no campo e compõe o campo
        #if abs(rb[0]) > self.world.xmaxmargin: self.world.goalpos = (-self.world.goalpos[0], self.world.goalpos[1])

        # Muda o campo no gol caso a bola esteja lá
        if self.world.ball.insideGoalArea():
            self.robot.vref = 0
            self.robot.field = UVFDefault(self.world, pose, rr, direction=-np.sign(rb[1]), radius=0, Kr=Kr)

        if any(np.abs(ra[:2]) > self.world.marginLimits) and any(np.abs(rb) > self.world.marginLimits):
            self.robot.field = UVFDefault(self.world, (pose[0]-max(0.20, (rb[0]-ra[0]) + 0.20), pose[1], 0), rr, direction=-np.sign(rb[1]), Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va)

        elif any(np.abs(rb) > self.world.marginLimits):
            self.robot.field = UVFDefault(self.world, (*pose[:2], 0), rr, direction=-np.sign(rb[1]), Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va)
        else: 
            #if howFrontBall(rb, rr, rg) > 0: radius = 0
            #else: radius = None
            self.robot.field = UVFDefault(self.world, pose, rr, direction=0, Kr=Kr, singleObstacle=singleObstacle, Vr=vr, Po=ra, Vo=va)