from .elements import *
import logging
import time
import math

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
    def __init__(self, n_robots=3, side=1, vss=None, team_yellow=False, immediate_start=False, control=False, debug=False, referee=False,mirror=False):
        self.n_robots = n_robots
        self._team = [TeamRobot(self, i, on=immediate_start)
                      for i in range(self.n_robots)]
        # self.enemies = [TeamRobot(self, i, on=immediate_start) for i in range(self.n_robots)]
        self.ball = Ball(self)
        self.field = Field(side)
        self.vss = vss
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
            # blue = self.enemies
        else:
            # yellow = self.enemies
            blue = self.team

        robot_id = 0
        
        if self.mirror: 
            if self.debug:
                print("UTILIZANDO CAMPO INVERTIDO")
            mirror = (-1,np.pi)
        else: 
            if self.debug:
                print("UTILIZANDO CAMPO SEM INVERSÃO")
            mirror = (1,0)
        
        if self.team_yellow:
            
            team = message.robots_yellow
            for _ in team:
                # Pela vsss vision recebemos em mm e nossa estrategia usa m

                if self.debug:
                    print(f"Yellow - {robot_id} | x {(message.robots_yellow[robot_id].x) / (1000*mirror[0]):.2f} | y {(message.robots_yellow[robot_id].y) / (1000*mirror[0]):.2f} | th {(message.robots_yellow[robot_id].orientation)+mirror[1]:.2f}")
                    
                yellow[robot_id].update(
                    message.robots_yellow[robot_id].x / (1000*mirror[0]),
                    message.robots_yellow[robot_id].y / (1000*mirror[0]),
                    message.robots_yellow[robot_id].orientation + mirror[1]
                )
            robot_id += 1
        else:
            team = message.robots_blue
    
            for _ in team:

                if self.debug:
                    print(f"Blue - {robot_id} | x {(message.robots_blue[robot_id].x) / (1000*mirror[0]):.2f} | y {(message.robots_blue[robot_id].y) / (1000*mirror[0]):.2f} | th {(message.robots_blue[robot_id].orientation + mirror[1]):.2f}")
                    
                blue[robot_id].update(
                    message.robots_blue[robot_id].x / (1000*mirror[0]),
                    message.robots_blue[robot_id].y / (1000*mirror[0]),
                    message.robots_blue[robot_id].orientation+mirror[1]
                )
            robot_id+=1

        if self.mirror:
            
            self.ball.update((message.balls[0].x) / -1000, (message.balls[0].y) / -1000)
            
            if self.debug:
                print(f"bola {(message.balls[0].x/-1000):.2f} {(message.balls[0].y / -1000):.2f}")
                
        else:
            self.ball.update((message.balls[0].x) /1000, (message.balls[0].y) / 1000)
            if self.debug:
                print(f"bola {(message.balls[0].x/1000):.2f} {(message.balls[0].y / 1000):.2f}")
        
        

        # self.manualControlSpeedV = message["manualControlSpeedV"]
        # self.manualControlSpeedW = message["manualControlSpeedW"]
        # logging.info("Vision update.")

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
