from abc import ABC, abstractmethod
from .entity.attacker import Attacker
from .entity.goalKeeper import GoalKeeper
from .entity.defender import Defender
from .entity.midfielder import Midfielder
from .entity.controlTest import ControlTester
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
    def __init__(self, world, static_entities=False):
        super().__init__(world)

        # States
        self.currentAttacker = None
        self.currentDefender = None

        # Variables
        self.static_entities = static_entities

    def manageReferee(self, arp, command):

        # Pegar apenas id que existe dos robos
        robot_id = []
        for robot in self.world.team:
            if robot is None:
                return
        for robot in self.world.team:
            if robot is not None:
                robot_id.append(robot.id)

        if command is None: 
            for robot in self.world.raw_team: 
                if robot is not None:
                    robot.turnOff()
        

        
        else:
            self.goalkeeperIndx = None
            self.AttackerIdx = None
            if command.foul == Foul.KICKOFF:
                
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                    else:
                        for robot in self.world.raw_team: 
                            if robot is not None:
                                robot.turnOff()
                else:
                    if self.world.field.side == 1:
                        for robot in self.world.raw_team: 
                            if robot is not None:
                                robot.turnOff()
                    
                    else:
                        for robot in self.world.raw_team: 
                            if robot is not None:
                                robot.turnOff()
             # Pausa jogo
            elif command.foul == Foul.STOP or command.foul == Foul.HALT:
                
                if(self.world.debug):
                    print("COMANDO STOP OU HALT ENVIADO")
                
                for robot in self.world.raw_team: 
                    if robot is not None:
                        robot.turnOff()
                    
            elif command.foul == Foul.PENALTY_KICK:
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()                 
                else:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
            
            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_1:
                if(self.world.debug):
                    print("FREE BALL Q1")
                if self.world.field.side == 1:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                else: 
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
            
            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_2:
                
                if(self.world.debug):
                    print("FREE BALL Q2")

                if self.world.field.side == 1:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                else: 
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()

            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_3:
                
                if(self.world.debug):
                    print("FREE BALL Q2")
                    
                if self.world.field.side == 1:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                else: 
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()    

            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_4:
                
                if(self.world.debug):
                    print("FREE BALL Q4")
                    
                if self.world.field.side == 1:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                else: 
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()

            elif command.foul == Foul.GOAL_KICK:
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()
                else:
                    for robot in self.world.raw_team: 
                        if robot is not None:
                            robot.turnOff()           
                    
            # Inicia jogo
            elif command.foul == Foul.GAME_ON:
                
                if(self.world.debug):
                    print("COMANDO START ENVIADO")
                
                for robot in self.world.raw_team:
                    if robot is not None:
                        robot.turnOn()
    
    def nearestGoal(self, indexes):
        rg = np.array([-1.1, 0])
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
        if self.world.ball.pos[0] < -0.35:
            return [GoalKeeper, Defender, Defender, Defender, Attacker]
        else:
            return [GoalKeeper,Defender, Midfielder, Attacker, Attacker]

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

    def update(self, world):

        #Como estamos trabalhando a partir de um número dado de quantos robôs temos, é melhor tratar esses updates em um ciclo
        #De repetição que tem range máximo o número de robôs e atualizaremos com base na prioridade (goleiro primeiro, atacante segundo) 
        #obs: (ficará comentado o que era antes)
        if self.static_entities:
            roles=[Attacker, GoalKeeper, Midfielder, Midfielder, Attacker]
            if self.world.staticen is False:
                for robo in self.world.n_robots:
                    self.world.team[int(robo)].updateEntity(roles[int(robo)])
                    self.world.staticen = True
            #self.world.team[0].updateEntity(Attacker)
            #self.world.team[1].updateEntity(Defender)
            #self.world.team[2].updateEntity(GoalKeeper)

        #mesma coisa aqui só que sem o static-entities
        # elif world.control:
        #     for i in self.world.n_robots:
        #         self.world.team[i].updateEntity(ControlTester, forced_update=True)
        #     #self.world.team[0].updateEntity(ControlTester, forced_update=True)
        #     #self.world.team[1].updateEntity(ControlTester, forced_update=True)
        #     #self.world.team[2].updateEntity(ControlTester, forced_update=True)

        else:
            formation = self.formationDecider()
            toDecide = self.availableRobotIndexes()

            if GoalKeeper in formation and len(toDecide) >= 5:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)

            if Defender in formation and len(toDecide) >= 3:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            if Defender in formation and len(toDecide) >= 3:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            hasMaster = False
            if Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestMasterAttackerBetweenTwo(formation, toDecide)
                hasMaster = True
            
            if Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                toDecide.remove(toDecide[0])
                formation.remove(Attacker)
            if Midfielder in formation and len(toDecide) >= 1:
                self.world.team[toDecide[0]].updateEntity(Midfielder)
                toDecide.remove(toDecide[0])
                formation.remove(Midfielder)

        for robot in self.world.team:
            if robot is not None:
                robot.updateSpin()
                if robot.entity is not None:
                    robot.entity.fieldDecider()
                    robot.entity.directionDecider()
                    print(f'\n\n{robot.entity}\n')