from abc import ABC, abstractmethod
from .entity.attacker import Attacker
from .entity.goalKeeper import GoalKeeper
from .entity.defender import Defender
from .entity.midfielder import Midfielder
from .entity.controlTest import ControlTester
from .entity.SecAttacker import SecAttacker
from .entity.AI_attacker import AI_Attacker
from client.protobuf.vssref_common_pb2 import Foul, Quadrant
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
    def __init__(self, world, static_entities=False, AI_attacker=False):
        super().__init__(world)

        # States
        self.currentAttacker = None
        self.currentDefender = None

        # Variables
        self.static_entities = static_entities

        # AI
        self.AI_attacker = AI_attacker

    def manageReferee(self, command):
        if command is None: 
            for robot in self.world.raw_team: 
                if robot is not None:
                    robot.turnOff()
        
        else:

            ComandoReferee = {
                Foul.KICKOFF:"Começo de jogo",
                Foul.FREE_BALL:"Free ball",
                Foul.PENALTY_KICK:"Pênaulti",
                Foul.GOAL_KICK:"Tiro de meta",
                Foul.GAME_ON:"Start",
                Foul.STOP:"Stop",
                Foul.HALT:"Stop"
            }

            if self.world.debug:
                print(f'{ComandoReferee[command.foul]} no quadrante {command.foulQuadrant}')
            [robot.turnOn() for robot in self.world.team if robot is not None and ComandoReferee[command.foul] == "Start"] + [robot.turnOff() for robot in self.world.team if robot is not None and ComandoReferee[command.foul] != "Start"]
                    
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
        if self.world.ball.pos[0] < -0.25 and not self.AI_attacker:
            return [GoalKeeper, Attacker, Attacker]
        elif self.world.ball.pos[0] < -0.25:
            return [GoalKeeper, Defender, AI_Attacker]
        elif self.AI_attacker:
            return [Defender, Attacker, AI_Attacker]
        else:
            return [Defender, Attacker, Attacker]

    #alteramos para que ToDecide (a variável que instancia esta função) esteja em formato de lista e não em um np.ndarray
    def availableRobotIndexes(self):
        return self.world.n_robots.copy()

    def decideBestGoalKeeper(self, formation, toDecide):
        nearest = self.nearestGoal(toDecide)
        self.world.team[nearest].updateEntity(GoalKeeper)
        
        toDecide.remove(nearest)
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

    def decideBestAI_AttackerBetweenTwo(self, formation, toDecide):
        d1 = norm(self.world.team[toDecide[0]].pos, self.world.ball.pos)
        d2 = norm(self.world.team[toDecide[1]].pos, self.world.ball.pos)

        self.currentAttacker = bestWithHyst(self.currentAttacker, toDecide, [d1, d2], 0.20)
        if self.behind_ball(self.world.ball.pos, self.world.team[self.currentAttacker].pos) < 0:
            self.world.team[self.currentAttacker].updateEntity(Attacker)
            toDecide.remove(self.currentAttacker)
        # elif not self.behind_ball(self.world.team[self.currentAttacker].pos, self.world.ball.pos):
        #     self.world.team[self.currentAttacker].updateEntity(Attacker)
        #     toDecide.remove(self.currentAttacker)
        else:
            self.world.team[self.currentAttacker].updateEntity(AI_Attacker)
            toDecide.remove(self.currentAttacker)
        formation.remove(AI_Attacker)

        return formation, toDecide
    
    def behind_ball(self, ball, robot):
        if ball[0] > 0.5 and abs(ball[1]) > 0.3: ball_shift = 0
        else: ball_shift = 0.2
        ball_pos = np.array([ball[0] - ball_shift, ball[1]])
        robot_pos = np.array([robot[0], robot[1]])
        goal_pos = np.array([(self.world.field.width)/2 - 0.1, 0])  # Opponent's goal center

        # 1. Positional Alignment Reward -------------------------------------------
        # Vector calculations
        ball_to_goal = goal_pos - ball_pos
        ball_to_robot = ball_pos - robot_pos
        
        # Normalize vectors
        ball_to_goal_norm = ball_to_goal / np.linalg.norm(ball_to_goal)
        robot_to_ball_norm = ball_to_robot / np.linalg.norm(ball_to_robot)

        # 1. Positional Reward (being behind the ball relative to goal)
        pos_alignment = np.dot(robot_to_ball_norm, ball_to_goal_norm)
        return pos_alignment

    def update(self, world):
        

        #Como estamos trabalhando a partir de um número dado de quantos robôs temos, é melhor tratar esses updates em um ciclo
        #De repetição que tem range máximo o número de robôs e atualizaremos com base na prioridade (goleiro primeiro, atacante segundo) 
        #obs: (ficará comentado o que era antes)
        if self.static_entities:
            if self.AI_attacker:
                roles=[AI_Attacker,GoalKeeper,Defender]
            else:
                roles=[Attacker,Defender,Attacker]
            for robo in self.world.n_robots:
                self.world.team[robo].updateEntity(roles[robo])
            #self.world.team[0].updateEntity(Attacker)
            #self.world.team[1].updateEntity(Defender)
            #self.world.team[2].updateEntity(GoalKeeper)

        #mesma coisa aqui só que sem o static-entities
        elif world.control:
            for i in self.world.n_robots:
                self.world.team[i].updateEntity(ControlTester)
            #self.world.team[0].updateEntity(ControlTester, forced_update=True)
            #self.world.team[1].updateEntity(ControlTester, forced_update=True)
            #self.world.team[2].updateEntity(ControlTester, forced_update=True)

        else:
            formation = self.formationDecider()
            toDecide = self.availableRobotIndexes()
            
            if AI_Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                if (abs(self.world.ball.pos[0]) > self.world.field.width/2 - 0.2\
                or abs(self.world.ball.pos[1]) > self.world.field.height/2 - 0.1):
                    self.world.team[toDecide[0]].updateEntity(AI_Attacker)
                    toDecide.remove(toDecide[0])
                elif self.behind_ball(self.world.ball.pos, self.world.team[toDecide[0]].pos) < 0:#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                    self.world.team[toDecide[0]].updateEntity(Attacker)
                    toDecide.remove(toDecide[0])
                # elif not self.behind_ball(self.world.team[toDecide[0]].pos, self.world.ball.pos):#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                #     self.world.team[toDecide[0]].updateEntity(Attacker)
                #     toDecide.remove(toDecide[0])
                else:
                    self.world.team[toDecide[0]].updateEntity(AI_Attacker)
                    toDecide.remove(toDecide[0])
                formation.remove(AI_Attacker)

            if GoalKeeper in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)
            
            hasMaster = False
            if AI_Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestAI_AttackerBetweenTwo(formation, toDecide)
                hasMaster = True

            if Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestMasterAttackerBetweenTwo(formation, toDecide)
                hasMaster = True

            if Defender in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            
            if AI_Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                
                if self.behind_ball(self.world.ball.pos, self.world.team[toDecide[0]].pos) < 0:#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                    self.world.team[toDecide[0]].updateEntity(Attacker)
                    toDecide.remove(toDecide[0])
                # elif not self.behind_ball(self.world.team[toDecide[0]].pos, self.world.ball.pos):#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                #     self.world.team[toDecide[0]].updateEntity(Attacker)
                #     toDecide.remove(toDecide[0])
                else:
                    self.world.team[toDecide[0]].updateEntity(AI_Attacker)
                    toDecide.remove(toDecide[0])
                formation.remove(AI_Attacker)

            if Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                self.world.team[toDecide[0]].updateEntity(Attacker)
                toDecide.remove(toDecide[0])
                formation.remove(Attacker)
        for robot in self.world.team:
            if robot is not None:
                robot.updateSpin()
                if robot.entity is not None:
                    robot.entity.fieldDecider()
                    robot.entity.directionDecider()