from .elements import *
import logging
import time
import math
import constants

class Field:
    def __init__(self, side):
        self.width = 1.75
        self.height = 1.35
        self.goalAreaWidth = 0.15
        self.goalAreaHeight = 0.70

        self.xmargin = 0.30
        self.ymargin = 0.18
        self.side = side

        self.areaEllipseSize = (0.35, 0.52)
        self.areaEllipseCenter = (-self.maxX + 0.10, 0)

    @property
    def maxX(self):
        return self.width / 2

    @property
    def maxY(self):
        return self.height / 2

    @property
    def size(self):
        return (self.maxX, self.maxY)

    @property
    def marginX(self):
        return self.maxX - self.xmargin

    @property
    def marginY(self):
        return self.maxY - self.ymargin

    @property
    def marginPos(self):
        return (self.marginX, self.marginY)

    @property
    def goalPos(self):
        return (self.maxX, 0)

    @property
    def goalAreaSize(self):
        return (self.goalAreaWidth, self.goalAreaHeight)
class World:
    def __init__(self, n_robots=3, side=1, FIRASim=False, team_yellow=False, immediate_start=False, control=False, debug=False, referee=False ,mirror=False):
        self.n_robots = n_robots
        self._team = [TeamRobot(self, i, on=immediate_start)
                      for i in range(self.n_robots)]
        # self.enemies = [TeamRobot(self, i, on=immediate_start) for i in range(self.n_robots)]
        self.ball = Ball(self)
        self.field = Field(side)
        self.FIRASim = FIRASim
        self.team_yellow = team_yellow
        self.allyGoals = 0
        self.enemyGoals = 0
        self.updateCount = 0
        self.manualControlSpeedV = 0
        self.manualControlSpeedW = 0
        self.control = control
        self.referee = referee
        self.debug = debug
        self.mirror = mirror

    def update(self, message):
        
        if self.team_yellow: 
            yellow = self.team
        else:
            blue = self.team
            
        if self.mirror: 
            if self.debug:
                print("UTILIZANDO CAMPO INVERTIDO")
            mirror = (-1,np.pi)
        else: 
            if self.debug:
                print("UTILIZANDO CAMPO SEM INVERSÃO")
            mirror = (1,0)
        

        if self.team_yellow:            
                
            for robot in message.frame.robots_yellow:
                
                if self.debug:
                    print(f"Yellow - {robot.robot_id} | x {(robot.x*mirror[0]):.2f} | y {(robot.y*mirror[0]):.2f} | th {(robot.orientation+mirror[1]):.2f}")

                yellow[robot.robot_id].update(
                        robot.x*mirror[0], 
                        robot.y*mirror[0], 
                        robot.orientation+mirror[1]
            )
                
        else:

            for robot in message.frame.robots_blue:
        
                
                if self.debug:
                    print(f"Blue - {robot.robot_id} | x {(robot.x*mirror[0]):.2f} | y {(robot.y*mirror[0]):.2f} | th {(robot.orientation+mirror[1])}")
                        

                blue[robot.robot_id].update(
                    robot.x*mirror[0], 
                    robot.y*mirror[0], 
                    robot.orientation+mirror[1],
                )

        self.ball.update(message.frame.ball.x*mirror[0], message.frame.ball.y*mirror[0])

        self.updateCount += 1
        
    def FIRASim_update(self, message):
        # teamPos = zip(message["ally_x"], message["ally_y"], message["ally_th"], message["ally_vx"], message["ally_vy"], message["ally_w"])
        # enemiesPos = zip(message["enemy_x"], message["enemy_y"], message["enemy_th"], message["enemy_vx"], message["enemy_vy"], message["enemy_w"])

        if self.team_yellow: 
            yellow = self.team
        else:
            blue = self.team
        if self.team_yellow:
            robot_id = 0
            for robot in message.frame.robots_yellow:
                #yellow[robot_id].update(message.robots_yellow[robot_id].x,message.robots_yellow[robot_id].y, message.robots_yellow[robot_id].orientation)
                yellow[robot_id].update(robot.x, robot.y, robot.orientation)
                robot_id += 1
        else:
            robot_id = 0
            for robot in message.frame.robots_blue:
                blue[robot_id].update(robot.x, robot.y, robot.orientation)
                robot_id += 1
        # for robot, pos in zip(self.team, teamPos): robot.update(*pos)
        # for robot, pos in zip(self.enemies, enemiesPos): robot.update(*pos)
        #self.ball.update(message["ball_x"], message["ball_y"], message["ball_vx"], message["ball_vy"])
        self.ball.update(message.frame.ball.x, message.frame.ball.y)

        self.updateCount += 1

    def addAllyGoal(self):
        print("Gol aliado!")
        self.allyGoals += 1

    def addEnemyGoal(self):
        print("Gol inimigo!")
        self.enemyGoals += 1

    @property
    def goals(self):
        return self.allyGoals + self.enemyGoals

    @property
    def balance(self):
        return self.allyGoals - self.enemyGoals

    @property
    def team(self):
        return self._team  # [robot for robot in self._team if robot.on]

    @property
    def raw_team(self):
        return self._team
