from .elements import *
import logging

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
    def __init__(self, n_robots=3, side=1, vss=None, team_yellow=False, immediate_start=False, control=False):
        self.n_robots = n_robots
        self._team = [TeamRobot(self, i, on=immediate_start) for i in range(self.n_robots)]
        self.enemies = [TeamRobot(self, i, on=immediate_start) for i in range(self.n_robots)]
        self.ball = Ball(self)
        self.field = Field(side)
        self.vss = vss
        self.team_yellow = team_yellow
        self.allyGoals = 0
        self.enemyGoals = 0
        self.updateCount = 0
        self.checkBatteries = False
        self.manualControlSpeedV = 0
        self.manualControlSpeedW = 0
        self.control = control
        
    def update(self, message):
        logging.info(message)
        if self.team_yellow: 
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        robot_id = 0

        if self.team_yellow:
            team = message.robots_yellow
            for _ in team:
                yellow[robot_id].update(
                    message.robots_yellow[robot_id].x,
                    message.robots_yellow[robot_id].y,
                    message.robots_yellow[robot_id].orientation
                )
                robot_id+=1
        else:
            team = message.robots_yellow
            for _ in team:
                blue[robot_id].update(
                    message.robots_blue[robot_id].x,
                    message.robots_blue[robot_id].y,
                    message.robots_blue[robot_id].orientation
                )
                robot_id+=1
        self.ball.update(message.balls[0].x, message.balls[0].y)
        # self.checkBatteries = message["check_batteries"]
        # self.manualControlSpeedV = message["manualControlSpeedV"]
        # self.manualControlSpeedW = message["manualControlSpeedW"]
        logging.info("Vision update.")
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
        return self._team#[robot for robot in self._team if robot.on]

    @property
    def raw_team(self):
        return self._team