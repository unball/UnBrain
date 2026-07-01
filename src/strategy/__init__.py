from abc import ABC, abstractmethod
from .entity.attacker import Attacker
from .entity.goalKeeper import GoalKeeper
from .entity.defender import Defender
from .entity.midfielder import Midfielder
from .entity.testers.controlTest import ControlTester
from .entity.testers.controlTestRobust import ControlTesterRobust
from .entity.SecAttacker import SecAttacker
from .entity.AI_attacker import AI_Attacker
from .entity.testers.GoalKeeperTester import GoalKeeperTester
from .entity.testers.DefenderTester import DefenderTester
from .entity.testers.AttackerTester import AttackerTester
from .entity.testers.MidfielderTester import MidfielderTester
from .entity.testers.AI_AttackerTester import AI_AttackerTester
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
    def manageReferee(self, command):
        pass

    @abstractmethod
    def update(self):
        pass

class MainStrategy(Strategy):
    def __init__(self, world, static_entities=False, AI_attacker=False):
        super().__init__(world)
        self.iniciando = False

        # States
        self.currentAttacker = None
        self.currentDefender = None
        self.currentGoalkeeper = None
        self._last_formation_defense = False

        # Variables
        self.static_entities = static_entities

        # AI
        self.AI_attacker = AI_attacker

    def getEntity(self, entity):
        return entity.__class__.__name__

    def resolveForcedEntity(self, role_str):
        role_map = {
            'Atacante': (Attacker, {}),
            'Attacker': (Attacker, {'slave': True}),
            'MasterAttacker': (Attacker, {'slave': False}),
            'Zagueiro': (Defender, {}),
            'Defender': (Defender, {}),
            'Goleiro': (GoalKeeper, {}),
            'GoalKeeper': (GoalKeeper, {}),
            'Meio Campo': (Midfielder, {}),
            'MidFielder': (Midfielder, {}),
            'Midfielder': (Midfielder, {}),
            'Sec_Attacker': (SecAttacker, {}),
            'SecAttacker': (SecAttacker, {}),
            'AI': (AI_Attacker, {}),
            'AI_Attacker': (AI_Attacker, {}),
            'GoalKeeperTester': (GoalKeeperTester, {}),
            'DefenderTester': (DefenderTester, {}),
            'AttackerTester': (AttackerTester, {}),
            'MidfielderTester': (MidfielderTester, {}),
            'AI_AttackerTester': (AI_AttackerTester, {}),
            'MeioCampoZagueiro': (Defender, {}),
            'AtacanteZagueiro': (Defender, {}),
            'AtacanteMeioCampo': (Attacker, {}),
        }
        return role_map.get(role_str)

    def updateRobotWithForcedEntity(self, robot, role_str):
        resolved = self.resolveForcedEntity(role_str)
        if resolved is None:
            return False

        entity_class, kwargs = resolved
        robot.updateEntity(entity_class, **kwargs)
        return True

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
        rg = np.array([-self.world.field.maxX, 0])
        rrs = np.array([self.world.team[i].pos for i in indexes])
        nearest = indexes[np.argmin(np.linalg.norm(rrs-rg, axis=1))]

        return nearest

    def getEntity(self, robot):
        if self.world.team[robot].entity != None:
            return self.world.team[robot].entity.__class__.__name__
        else:
            return None

    def ellipseTarget(self):
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rr = np.array([0,0,0]) # dummy, usado para computar angulo do pose, não é necessário aqui
        
        pose, spin = blockBallElipse(rb, vb, rr, self.world.field.areaEllipseCenter, *self.world.field.areaEllipseSize)

        return pose[:2]

    def formationDecider(self):
        defense_threshold = -self.world.field.maxX / 3
        if self._last_formation_defense:
            defense_threshold += 0.15  # Histerese para evitar a troca rápida de papéis

        is_defense = self.world.ball.pos[0] < defense_threshold
        self._last_formation_defense = is_defense

        if is_defense and not self.AI_attacker:
            return [GoalKeeper, Attacker, Attacker]
        elif is_defense:
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
        self.currentGoalkeeper = nearest
        self.world.team[nearest].updateEntity(GoalKeeper)
        
        toDecide.remove(nearest)
        formation.remove(GoalKeeper)
        
        return formation, toDecide

    def decideBestDefender(self, formation, toDecide):
        old_formation = self.formationDecider()
        if not GoalKeeper in old_formation and self.currentGoalkeeper != None:
            self.currentDefender = self.currentGoalkeeper
            self.world.team[self.currentDefender].updateEntity(Defender)
            if self.currentDefender in toDecide:
                toDecide.remove(self.currentDefender)
            formation.remove(Defender)
        else:
            target = self.ellipseTarget()
            distances = [norm(target, self.world.team[robotIndex].pos) for robotIndex in toDecide]

            self.currentDefender = bestWithHyst(self.currentDefender, toDecide, distances, 0.20)
            self.world.team[self.currentDefender].updateEntity(Defender)

            toDecide.remove(self.currentDefender)
            formation.remove(Defender)

        return formation, toDecide

    def decideBestMasterAttacker(self, formation, toDecide):
        d = [norm(self.world.team[i].pos, self.world.ball.pos) for i in toDecide]
        

        self.currentAttacker = bestWithHyst(self.currentAttacker, toDecide, d, 0.20)
        if self.world.team[self.currentAttacker].entity != None and self.getEntity(self.currentAttacker) == 'Attacker':
            if self.world.team[self.currentAttacker].entity.slave == False:
                self.world.team[self.currentAttacker].updateEntity(Attacker, ballShift=0, slave=False)
            elif self.world.team[self.currentAttacker].entity.slave == True:
                self.world.team[self.currentAttacker].updateEntity(Attacker, ballShift=0, slave=True)
        else:
            self.world.team[self.currentAttacker].updateEntity(Attacker, ballShift=0, slave=False)
        toDecide.remove(self.currentAttacker)
        formation.remove(Attacker)

        return formation, toDecide

    def decideBestAI_AttackerBetweenTwo(self, formation, toDecide):
        d1 = norm(self.world.team[toDecide[0]].pos, self.world.ball.pos)
        d2 = norm(self.world.team[toDecide[1]].pos, self.world.ball.pos)

        self.currentAttacker = bestWithHyst(self.currentAttacker, toDecide, [d1, d2], 0.20)
        if self.world.ball.pos[0] < -self.world.field.maxX * 0.4:
            self.world.team[self.currentAttacker].updateEntity(Attacker)
            toDecide.remove(self.currentAttacker)
        elif self.behind_ball(self.world.ball.pos, self.world.team[self.currentAttacker].pos) < 0:
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
        if robot[0] > ball[0] - self.world.field.maxX * 0.4:
            return -1
        else:
            return 1
        # if ball[0] > 0.5 and abs(ball[1]) > 0.3: ball_shift = 0
        # else: ball_shift = 0.2
        # ball_pos = np.array([ball[0] - ball_shift, ball[1]])
        # robot_pos = np.array([robot[0], robot[1]])
        # goal_pos = np.array([(self.world.field.width)/2 - 0.1, 0])  # Opponent's goal center

        # # 1. Positional Alignment Reward -------------------------------------------
        # # Vector calculations
        # ball_to_goal = goal_pos - ball_pos
        # ball_to_robot = ball_pos - robot_pos
        
        # # Normalize vectors
        # ball_to_goal_norm = ball_to_goal / np.linalg.norm(ball_to_goal)
        # robot_to_ball_norm = ball_to_robot / np.linalg.norm(ball_to_robot)

        # # 1. Positional Reward (being behind the ball relative to goal)
        # pos_alignment = np.dot(robot_to_ball_norm, ball_to_goal_norm)
        # return pos_alignment

    def update(self, world):
        # Sincroniza dinamicamente as flags da Interface (UI) com o estado interno da estratégia
        is_enemy = getattr(world, 'enemy_ai', False)
        if is_enemy:
            self.AI_attacker = getattr(world, 'flag_enemy_ai', self.AI_attacker)
        else:
            self.AI_attacker = getattr(world, 'flag_ppo_ai', self.AI_attacker)
        if self.iniciando == False and self.AI_attacker:
            robot = self.world.team[self.world.n_robots[0]]
            robot.updateEntity(AI_Attacker)
            robot.entity._control.output(robot)
            self.iniciando = True

        #Como estamos trabalhando a partir de um número dado de quantos robôs temos, é melhor tratar esses updates em um ciclo
        #De repetição que tem range máximo o número de robôs e atualizaremos com base na prioridade (goleiro primeiro, atacante segundo) 
        #obs: (ficará comentado o que era antes)
        
        if getattr(self.world, 'teleport_mode', None) is not None:
            from .entity.teleport import TeleportEntity
            formation_name = self.world.teleport_mode
            config = self.world.teleport_config.get(formation_name, [])
            
            targets = []
            if isinstance(config, dict):
                for k in sorted(list(config.keys())):
                    targets.append(config[k])
            else:
                targets = config
            
            available_robots = list(self.world.n_robots)
            assigned_targets = {}
            
            for pos in targets:
                if pos is None: continue
                
                best_robot = None
                best_dist = float('inf')
                target_np = np.array([pos['x'], pos['y']])
                
                for robo_idx in available_robots:
                    if self.world.team[robo_idx] is not None:
                        dist = np.linalg.norm(np.array(self.world.team[robo_idx].pos) - target_np)
                        if dist < best_dist:
                            best_dist = dist
                            best_robot = robo_idx
                
                if best_robot is not None:
                    assigned_targets[best_robot] = pos
                    available_robots.remove(best_robot)
            
            for robo_idx in self.world.n_robots:
                if robo_idx in assigned_targets:
                    pos = assigned_targets[robo_idx]
                    self.world.team[robo_idx].updateEntity(TeleportEntity,forced_update=True, target_x=pos['x'], target_y=pos['y'], target_th=pos['th'])
                    print('update Entity')
                else:
                    # Se não há posição de teleporte para este robô, garante que ele não fique num estado de teleporte preso
                    if getattr(self.world.team[robo_idx], 'entity', None) and isinstance(self.world.team[robo_idx].entity, TeleportEntity):
                        self.world.team[robo_idx].entity = None
            
            for robot in self.world.team:
                if robot is not None:
                    robot.updateSpin()
                    if robot.entity is not None:
                        robot.entity.fieldDecider()
                        robot.entity.directionDecider()
            return

        else: 
            static_entities_active = getattr(world, 'flag_static_entities', getattr(world, 'static_entities', self.static_entities))
        if static_entities_active:
            static_ent_val = static_entities_active
            
            if hasattr(world, 'force_entities') and len(world.force_entities) > 0:
                for i, robo in enumerate(self.world.n_robots):
                    role_str = world.force_entities.get(str(robo))
                    if role_str:
                        self.updateRobotWithForcedEntity(self.world.team[robo], role_str)
                    else:
                        # Fallback apenas quando o robô não tem seleção explícita
                        default_roles = [Attacker, Defender, GoalKeeper]
                        if i < len(default_roles): self.world.team[robo].updateEntity(default_roles[i])
                        
            # 2. Command-line string parse
            elif isinstance(static_ent_val, str) and static_ent_val:
                roles = []
                for r in static_ent_val.split(','):
                    r = r.strip()
                    resolved = self.resolveForcedEntity(r)
                    if resolved is not None: roles.append(resolved)
                for i, robo in enumerate(self.world.n_robots):
                    if i < len(roles):
                        entity_class, kwargs = roles[i]
                        self.world.team[robo].updateEntity(entity_class, **kwargs)
                    
            # 3. Default fallback
            else:
                if self.AI_attacker:
                    roles=[AI_Attacker,GoalKeeper,Defender]
                else:
                    roles=[Attacker,Defender,GoalKeeper]
                for i, robo in enumerate(self.world.n_robots):
                    if i < len(roles): self.world.team[robo].updateEntity(roles[i])

        elif getattr(world, 'flag_control_tester', False):
            roles_map = {
                "ControlTester": ControlTester,
                "ControlTesterRobust": ControlTesterRobust,
                "AttackerTester": AttackerTester,
                "DefenderTester": DefenderTester,
                "GoalKeeperTester": GoalKeeperTester,
                "MidfielderTester": MidfielderTester,
                "AI_AttackerTester": AI_AttackerTester
            }
            test_roles = getattr(world, 'test_roles', ["None", "None", "None"])
            for i in self.world.n_robots:
                role_str = test_roles[i] if i < len(test_roles) else "None"
                if role_str in roles_map:
                    self.world.team[i].updateEntity(roles_map[role_str])
        else:
            formation = self.formationDecider()
            toDecide = self.availableRobotIndexes()

            if GoalKeeper in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)
         
            if Defender in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            if Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestMasterAttacker(formation, toDecide)
                hasMaster = True

            if AI_Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                if self.world.ball.pos[0] < -self.world.field.maxX * 0.4:
                    self.world.team[toDecide[0]].updateEntity(Attacker)
                    toDecide.remove(toDecide[0])
                elif (self.world.team[toDecide[0]].pos[1] - self.world.ball.pos[1]) < 0 and self.world.ball.pos[1] > 0 :#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                    self.world.team[toDecide[0]].updateEntity(Attacker)
                    toDecide.remove(toDecide[0])
                elif (self.world.team[toDecide[0]].pos[1] - self.world.ball.pos[1]) > 0 and self.world.ball.pos[1] < 0 :#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
                    self.world.team[toDecide[0]].updateEntity(Attacker)
                    toDecide.remove(toDecide[0])
                else:
                    self.world.team[toDecide[0]].updateEntity(AI_Attacker)
                    toDecide.remove(toDecide[0])
                formation.remove(AI_Attacker)

            # if AI_Attacker in formation and len(toDecide) >= 1:
            #     #possível erro na mudança de role abaixo, checar mais tarde
            #     # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True) 
            #     #pos atacante > self.world.field.maxY - 0.1
            #     if (abs(self.world.team[toDecide[0]].pos[0]) > self.world.field.width/2 - 0.1\
            #     or abs(self.world.team[toDecide[0]].pos[1]) > self.world.field.height/2 - 0.2):
            #         self.world.team[toDecide[0]].updateEntity(AI_Attacker)
            #         toDecide.remove(toDecide[0])
            #     elif self.behind_ball(self.world.ball.pos, self.world.team[toDecide[0]].pos) < 0 and not abs(self.world.team[toDecide[0]].pos[1]) :#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
            #         self.world.team[toDecide[0]].updateEntity(Attacker)
            #         toDecide.remove(toDecide[0])
            #     # elif not self.behind_ball(self.world.team[toDecide[0]].pos, self.world.ball.pos):#or (abs(self.world.ball.pos[1]) > 0.4 and self.world.team[toDecide[0]].pos[1] > 0.4)
            #     #     self.world.team[toDecide[0]].updateEntity(Attacker)
            #     #     toDecide.remove(toDecide[0])
            #     else:
            #         self.world.team[toDecide[0]].updateEntity(AI_Attacker)
            #         toDecide.remove(toDecide[0])
            #     formation.remove(AI_Attacker)

            if GoalKeeper in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestGoalKeeper(formation, toDecide)
            
            hasMaster = False
            if AI_Attacker in formation and len(toDecide) >= 2:
                formation, toDecide = self.decideBestAI_AttackerBetweenTwo(formation, toDecide)
                hasMaster = True

            if Defender in formation and len(toDecide) >= 1:
                formation, toDecide = self.decideBestDefender(formation, toDecide)

            
            if AI_Attacker in formation and len(toDecide) >= 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                # self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                if self.world.ball.pos[0] < -self.world.field.maxX * 0.4:
                    self.world.team[toDecide[0]].updateEntity(Attacker)
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

            if Attacker in formation and len(toDecide) == 1:
                #possível erro na mudança de role abaixo, checar mais tarde
                if self.world.team[toDecide[0]].entity != None and self.getEntity(toDecide[0]) == 'Attacker':
                    if self.world.team[toDecide[0]].entity.slave == False:
                        self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=False)
                    elif self.world.team[toDecide[0]].entity.slave == True:
                        self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                else:
                    self.world.team[toDecide[0]].updateEntity(Attacker, ballShift=0.15 if hasMaster else 0, slave=True)
                toDecide.remove(toDecide[0])
                formation.remove(Attacker)

        # Sobrescreve as entidades padrão com as entidades forçadas pela interface (se houver)
        force_entities_map = getattr(world, 'force_entities', {})
        if static_entities_active and force_entities_map:
            for robo_idx_str, role_str in force_entities_map.items():
                try:
                    robo_idx = int(robo_idx_str)
                    if robo_idx in self.world.n_robots:
                        self.updateRobotWithForcedEntity(self.world.team[robo_idx], role_str)
                except ValueError:
                    pass

        for robot in self.world.team:
            if robot is not None:
                robot.updateSpin()
                if robot.entity is not None:
                    robot.entity.fieldDecider()
                    robot.entity.directionDecider()
