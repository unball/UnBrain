from abc import ABC, abstractmethod
from .entity.attacker import Attacker
from .entity.goalKeeper import GoalKeeper
from .entity.defender import Defender
from .entity.midfielder import Midfielder
from .entity.controlTest import ControlTester
from .entity.SecAttacker import SecAttacker
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
            robot_id.append(robot.id)

        if command is None: 
            for robot in self.world.raw_team: 
                robot.turnOff()
        

        
        else:
            self.goalkeeperIndx = None
            self.AttackerIdx = None
            if command.foul == Foul.KICKOFF:
                
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    if self.world.field.side == 1:
                        rg = -np.array(self.world.field.goalPos)
                        rg[0] += 0.18

                        # posição do goleiro
                        positions = [(robot_id[0], (rg[0], rg[1], 0))]
                        positions.append((robot_id[1], (-0.3,  0, 0)))
                        positions.append((robot_id[2], (-0.2, 0, 0)))
                        arp.send(positions)
                    
                    else:
                        rg = -np.array(self.world.field.goalPos)
                        rg[0] += 0.18
                        # posição do goleiro
                        positions = [(robot_id[0], (rg[0], rg[1], 180))]
                        positions.append((robot_id[1], (0.3,  0, 180)))
                        positions.append((robot_id[2], (0.2, 0, 180)))
                        arp.send(positions)
                else:
                    if self.world.field.side == 1:
                        rg = -np.array(self.world.field.goalPos)
                        rg[0] += 0.18

                        # posição do goleiro
                        positions = [(robot_id[0], (rg[0], rg[1], 0))]
                        positions.append((robot_id[1], (-0.3,  0, 0)))
                        positions.append((robot_id[2], (-0.1, 0, 0)))
                        arp.send(positions)
                    
                    else:
                        rg = -np.array(self.world.field.goalPos)
                        rg[0] += 0.18
                        # posição do goleiro
                        positions = [(robot_id[0], (rg[0], rg[1], 180))]
                        positions.append((robot_id[1], (0.3,  0, 180)))
                        positions.append((robot_id[2], (0.1, 0, 180)))
                        arp.send(positions)
             # Pausa jogo
            elif command.foul == Foul.STOP or command.foul == Foul.HALT:
                
                if(self.world.debug):
                    print("COMANDO STOP OU HALT ENVIADO")
                
                for robot in self.world.raw_team: 
                    robot.turnOff()
                    
            elif command.foul == Foul.PENALTY_KICK:
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 90))]
                    positions.append((robot_id[1], (0,  0.30, 1.2*180)))
                    positions.append((robot_id[2], (0, -0.30, 0.8*180)))
                    arp.send(positions)                   
                else:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.2
                    positions = [(robot_id[0], (rg[0], rg[1], 90))]
                    penaltiPos = np.array([0.360, 0])
                    ang = 15 
                    robotPos = penaltiPos  - 0.065 * unit(ang*np.pi/180)
                    positions.append((robot_id[1], (robotPos[0],  robotPos[1], ang)))
                    positions.append((robot_id[2], (0, -0.30, 3)))
                    arp.send(positions)
            
            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_1:
                if(self.world.debug):
                    print("FREE BALL Q1")
                if self.world.field.side == 1:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]
                    positions.append((robot_id[1], (0.13, 0.4, 0)))
                    positions.append((robot_id[2], (0.08, -0.2, -0.2*(180/np.pi))))
                    arp.send(positions)
                else: 
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 180))]
                    positions.append((robot_id[1], (0.2, -0.16, 0 )))
                    positions.append((robot_id[2], (0.5, 0.4, -3*(180/np.pi)) ) ) 
                    arp.send(positions)
            
            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_2:
                
                if(self.world.debug):
                    print("FREE BALL Q2")

                if self.world.field.side == 1:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]
                    positions.append((robot_id[1], (-0.6, 0.4, 0)))
                    positions.append((robot_id[2], (-0.3, -0.15, -1.47*(180/np.pi)) ))
                    arp.send(positions)
                else: 
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 180))]
                    positions.append((robot_id[1], (-0.2, -0.26, 1.46*(180/np.pi))) )
                    positions.append((robot_id[2], (-0.18, 0.38, -3*(180/np.pi)) ) ) 
                    arp.send(positions)  

            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_3:
                
                if(self.world.debug):
                    print("FREE BALL Q2")
                    
                if self.world.field.side == 1:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]

                    positions.append((robot_id[1], (-0.56, -0.4, 0)))
                    positions.append((robot_id[2], (-0.3 , 0.1 , -1.47*(180/np.pi)) ))
                    arp.send(positions)
                else: 
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 180))]

                    positions.append((robot_id[1], (0.65 , 0.01 , 180 ) ))
                    positions.append((robot_id[2], (-0.16, -0.38 , -3*(180/np.pi)) ) ) 
                    arp.send(positions)    

            elif command.foul == Foul.FREE_BALL and command.foulQuadrant == Quadrant.QUADRANT_4:
                
                if(self.world.debug):
                    print("FREE BALL Q4")
                    
                if self.world.field.side == 1:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]

                    positions.append((robot_id[1], ( 0.14 , -0.38 , 0)))
                    positions.append((robot_id[2], ( 0.1 , 0.18 , -1.5*(180/np.pi)) ))
                    
                    arp.send(positions)
                else: 
                    
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 180))]

                    positions.append((robot_id[1], ( 0.23 , 0.1 , -1.6*(180/np.pi)) )) 
                    positions.append((robot_id[2], ( 0.57 , -0.37 , -3*(180/np.pi)) ) ) 
                    
                    arp.send(positions) 

            elif command.foul == Foul.GOAL_KICK:
                if RefereeCommands.color2side(command.teamcolor) != self.world.field.side:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]

                    positions.append((robot_id[1], (0.13,  -0.35 , -0.06*(180/np.pi)))) 
                    positions.append((robot_id[2], (0.2 , 0.1, 0)))
                    arp.send(positions)                   
                else:
                    rg = -np.array(self.world.field.goalPos)
                    rg[0] += 0.18
                    positions = [(robot_id[0], (rg[0], rg[1], 0))]
                    
                    positions.append((robot_id[0], ( 0.32 ,  -0.47 , -0.09*(180/np.pi)))) 
                    positions.append((robot_id[1], ( 0.65 ,  0.28 , 2.25*(180/np.pi)))) 
                    positions.append((robot_id[2], ( 0.45 , 0.27, -3*(180/np.pi))))
                    arp.send(positions)                  
                    
            # Inicia jogo
            elif command.foul == Foul.GAME_ON:
                
                if(self.world.debug):
                    print("COMANDO START ENVIADO")
                
                for robot in self.world.raw_team: 
                    robot.turnOn()
    
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
        if self.world.ball.pos[0] < -0.35:
            return [GoalKeeper, Attacker, Defender]
        else:
            return [GoalKeeper, Attacker, Attacker]

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
            roles=[Attacker,Attacker,SecAttacker]
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

            if GoalKeeper in formation:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)

            if Defender in formation and len(toDecide) >= 1:
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


        for robot in self.world.team:
            if robot is not None:
                robot.updateSpin()
                if robot.entity is not None:
                    robot.entity.fieldDecider()
                    robot.entity.directionDecider()