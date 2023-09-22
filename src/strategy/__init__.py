from abc import ABC, abstractmethod
from .entity.attacker import Attacker
from .entity.goalKeeper import GoalKeeper
from .entity.defender import Defender
from .entity.midfielder import Midfielder
from .entity.controlTest import ControlTester
#from client.protobuf.vssref_common_pb2 import Foul
from client.referee import RefereeCommands
from tools import sats, norml, unit, angl, angError, projectLine, howFrontBall, norm, bestWithHyst
from .movements import blockBallElipse
from copy import copy
import numpy as np
import time

class Strategy(ABC):
    def __init__(self, world):
        super().__init__()

        self.world = world

    @abstractmethod
    def manageReferee(self, rp, command):
        pass

    @abstractmethod
    def update(self):
        pass

class MainStrategy(Strategy):
    def __init__(self, world, static_entities=False):
        super().__init__(world)

        # States
        self.currentAttacker = None
        self.currentDefender = None

        # Variables
        self.static_entities = static_entities

    def manageReferee(self, rp, command):
        if command is None: return
        self.goalkeeperIndx = None
        self.AttackerIdx = None

        # Verifica gol
        if command.foul == Foul.KICKOFF:
            if RefereeCommands.color2side(command.teamcolor) == self.world.field.side:
                self.world.addEnemyGoal()
            elif RefereeCommands.color2side(command.teamcolor) == -self.world.field.side:
                self.world.addAllyGoal()

        elif command.foul == Foul.PENALTY_KICK:
            if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                rg = -np.array(self.world.field.goalPos)
                rg[0] += 0.18
                positions = [(0, (rg[0], rg[1], 90))]
                positions.append((1, (0,  0.30, 1.2*180)))
                positions.append((2, (0, -0.30, 0.8*180)))
                rp.send(positions)
            else:
                rg = -np.array(self.world.field.goalPos)
                rg[0] += 0.18
                positions = [(0, (rg[0], rg[1], 90))]
                penaltiPos = np.array([0.360, 0])
                ang = 15 
                robotPos = penaltiPos  - 0.065 * unit(ang*np.pi/180)
                positions.append((1, (robotPos[0],  robotPos[1], ang)))
                positions.append((2, (0, -0.30, 3)))
                rp.send(positions)

        # Inicia jogo
        elif command.foul == Foul.GAME_ON:
            for robot in self.world.raw_team: robot.turnOn()
            
        # Pausa jogo
        elif command.foul == Foul.STOP or command.foul == Foul.HALT:
            for robot in self.world.raw_team: robot.turnOff()
    
    def nearestGoal(self, indexes):
        rg = np.array([-0.75, 0])
        rrs = np.array([self.world.team[i].pos for i in indexes])
        nearest = indexes[np.argmin(np.linalg.norm(rrs-rg, axis=1))]

        return nearest

    def ellipseTarget(self):
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rr = np.array([0,0,0]) # dummy, usado para computar angulo do pose, não é necessário aqui
        
        pose, spin = blockBallElipse(rb, vb, rr, self.world.field.areaEllipseCenter, *self.world.field.areaEllipseSize)

        return pose[:2]

    def formationDecider(self):
        if self.world.ball.pos[0] < -0.45:
            return [GoalKeeper, Attacker, Defender]
        else:
            return [GoalKeeper, Attacker, Attacker]

    def availableRobotIndexes(self):
        return [0,1,2]

    def decideBestGoalKeeper(self, formation, toDecide):
        # nearest = self.nearestGoal(toDecide)
        # self.world.team[nearest].updateEntity(GoalKeeper)
        self.world.team[1].updateEntity(GoalKeeper)
        
        toDecide.remove(1)
        formation.remove(GoalKeeper)
        
        return formation, toDecide

    def decideBestDefender(self, formation, toDecide):
        target = self.ellipseTarget()
        distances = [norm(target, self.world.team[robotIndex].pos) for robotIndex in toDecide]

        self.currentDefender = bestWithHyst(self.currentDefender, toDecide, distances, 0.20)
        self.world.team[self.currentDefender].updateEntity(Defender)

        toDecide.remove(self.currentDefender)
        formation.remove(Defender)

        return formation, toDecide

    def decideBestMasterAttackerBetweenTwo(self, formation, toDecide):
        d1 = norm(self.world.team[toDecide[0]].pos, self.world.ball.pos)
        d2 = norm(self.world.team[toDecide[1]].pos, self.world.ball.pos)

        self.currentAttacker = bestWithHyst(self.currentAttacker, toDecide, [d1, d2], 0.20)
    
        self.world.team[self.currentAttacker].updateEntity(Attacker, ballShift=0, slave=False)
        toDecide.remove(self.currentAttacker)
        formation.remove(Attacker)

        return formation, toDecide

    def update(self):
        if self.static_entities:
            self.world.team[2].updateEntity(GoalKeeper)
            self.world.team[1].updateEntity(Attacker)
            self.world.team[0].updateEntity(Attacker)

        elif self.world.checkBatteries:
            self.world.team[2].updateEntity(Attacker)
            self.world.team[1].updateEntity(Attacker)
            self.world.team[0].updateEntity(ControlTester)

        else:
            formation = self.formationDecider()
            toDecide = self.availableRobotIndexes()

            if GoalKeeper in formation:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)

            if Defender in formation:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            hasMaster = False
            if Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestMasterAttackerBetweenTwo(formation, toDecide)
                hasMaster = True
            
            if Attacker in formation:
                self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.20 if hasMaster else 0, slave=True)
                toDecide.remove(toDecide[0])
                formation.remove(Attacker)


        for robot in self.world.team:
            robot.updateSpin()
            if robot.entity is not None:
                robot.entity.fieldDecider()
                robot.entity.directionDecider()