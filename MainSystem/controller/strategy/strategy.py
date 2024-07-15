from controller.strategy.entity import Attacker, GoalKeeper, Defender, MidFielder
from controller.tools import angl, angError, norm, unit
import numpy as np

class Strategy:
    def __init__(self, world, robots):
        self.robots = robots
        """Lista com os robôs a serem manipulados pela estratégia"""

        self.world = world
        self.state = 1
        self.midfielderState = 0
        self.histCenter = -0.15
        self.histSize = 0.1

    def run(self):
        # Decisor de entidades
        self.entityDecider()

        # Decisor de direção
        self.directionDecider()

        # Decisor de movimento
        self.movementDecider()

    def goodPositionToAttack(self, robot1, robot2):
        rb = np.array(self.world.ball.pos.copy())
        r0b = rb - np.array(robot1.pos)
        r1b = rb - np.array(robot2.pos)
        d0b = np.linalg.norm(r0b)
        d1b = np.linalg.norm(r1b)
        a0b = angError(angl(r0b), robot1.th)
        a1b = angError(angl(r1b), robot2.th)
        # Robô 0 é um bom atacante
        if (2*d0b < d1b and abs(a0b) < np.pi / 4 and abs(a0b) < abs(a1b)):
        #if not robot2.isAlive() or (2*d0b < d1b and abs(a0b) < np.pi / 4 and abs(a0b) < abs(a1b)):
            return 0
        # Robô 1 é um bom atacante
        #elif not robot1.isAlive() or (2*d1b < d0b and abs(a1b) < np.pi / 4 and abs(a1b) < abs(a0b)):
        elif (2*d1b < d0b and abs(a1b) < np.pi / 4 and abs(a1b) < abs(a0b)):
            return 1
        else:
        # Mantém o estado
            return -1

    def entityDecider(self):
        dynamicAttackerDefenderRobots = []
        dynamicAttackerMidFilderRobots = []
        dynamicMidfielderDefenderRobots = []
        firstAttacker = None
        for robot in self.robots:
            if robot.preferedEntity == "Atacante":
                if firstAttacker is None: firstAttacker = robot
                robot.entity = Attacker(self.world, robot)
            elif robot.preferedEntity == "Zagueiro":
                robot.entity = Defender(self.world, robot)
            elif robot.preferedEntity == "Goleiro":
                robot.entity = GoalKeeper(self.world, robot)
            elif robot.preferedEntity == "AtacanteZagueiro":
                dynamicAttackerDefenderRobots.append(robot)
            elif robot.preferedEntity == "AtacanteMeioCampo":
                dynamicAttackerMidFilderRobots.append(robot)
            elif robot.preferedEntity == "MeioCampoZagueiro":
                dynamicMidfielderDefenderRobots.append(robot)

        # Define um meio campo se houver um atacante
        if firstAttacker is not None:
            for robot in [r for r in self.robots if r.preferedEntity == "Meio Campo"]:
                robot.entity = MidFielder(self.world, robot, firstAttacker)
                
        #self.robots[0].entity = Defender(self.world, self.robots[0])
        #self.robots[1].entity = Attacker(self.world, self.robots[1])
        #TODO: Caso o atacante esteja parado (sem a bola), Defender vira atacante
        # if self.world.ball.pos[0] < 0:
        #     self.robots[1].entity = Attacker(self.world, self.robots[1])
        if len(dynamicAttackerDefenderRobots) == 2:
            self.attackerDefenderDecider(*dynamicAttackerDefenderRobots)
        
        if len(dynamicAttackerMidFilderRobots) == 2:
            self.attackerMidFilederDecider(*dynamicAttackerMidFilderRobots)

        if firstAttacker is not None:
            if len(dynamicMidfielderDefenderRobots) == 1:
                self.midfielderDefenderDecider(*dynamicMidfielderDefenderRobots, firstAttacker)

    def attackerDefenderDecider(self, *args):
        robot1, robot2 = args
        state = self.goodPositionToAttack(robot1, robot2)
        if state != -1:
            self.state = state
        if self.state == 0:
            robot1.entity = Attacker(self.world, robot1)
            robot2.entity = Defender(self.world, robot2)
        else:
            robot1.entity = Defender(self.world, robot1)
            robot2.entity = Attacker(self.world, robot2)

    def attackerMidFilederDecider(self, robot1, robot2):
        state = self.goodPositionToAttack(robot1, robot2)
        if state != -1:
            self.state = state
        if self.state == 0:
            robot1.entity = Attacker(self.world, robot1)
            robot2.entity = MidFielder(self.world, robot2, robot1)
        else:
            robot1.entity = MidFielder(self.world, robot1, robot2)
            robot2.entity = Attacker(self.world, robot2)

    def midfielderDefenderDecider(self, robot1, attackerRobot):
        rb = np.array(self.world.ball.pos.copy())
        vb = np.array(self.world.ball.vel.copy())

        delta = self.histSize * (1 - (np.arctan(vb[0] / 0.7) / (np.pi/2)))

        if rb[0]-self.histCenter > delta:
            self.midfielderState = 1
        elif rb[0]-self.histCenter < -delta:
            self.midfielderState = -1

        if self.midfielderState == 1:
            robot1.entity = MidFielder(self.world, robot1, attackerRobot)
        else:
            robot1.entity = Defender(self.world, robot1)
            attackerRobot.entity.setAuxRobot(robot1)

    def directionDecider(self):
        for robot in self.robots:
            if robot.entity is not None: robot.entity.directionDecider()

    def movementDecider(self):
        for robot in self.robots:
            if robot.entity is not None: robot.entity.movementDecider()