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
        self.checkBatteries = True
        self.manualControlSpeedV = 0
        self.manualControlSpeedW = 0
        self.control = control
        
    def update(self, message):
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
                # Pela vsss vision recebemos em mm e nossa estrategia usa m
                yellow[robot_id].update(
                    message.robots_yellow[robot_id].x / 1000,
                    message.robots_yellow[robot_id].y / 1000,
                    message.robots_yellow[robot_id].orientation * -1
                )
                robot_id+=1
        else:
            team = message.robots_blue
            for _ in team:
                # Pela vsss vision recebemos em mm e nossa estrategia usa m
                
                
                #print(message)
                print("x",(message.robots_blue[robot_id].x*-1) / 1000)
                print("y",(message.robots_blue[robot_id].y*-1) / 1000)
                print("th",(message.robots_blue[robot_id].orientation*-1))
                print("bola x",message.balls[0].x * -1 / 1000)
                print("bola y",message.balls[0].y * -1 / 1000)
                #exit()
                
                
                
                blue[robot_id].update(
                    (message.robots_blue[robot_id].x / 1000 )* -1,
                    (message.robots_blue[robot_id].y / 1000) * -1,
                    (message.robots_blue[robot_id].orientation) * 1
                    
                )
                robot_id+=1
        self.ball.update((message.balls[0].x * -1) / 1000 , (message.balls[0].y * -1)/ 1000 )
        # self.checkBatteries = message["check_batteries"]
        # self.manualControlSpeedV = message["manualControlSpeedV"]
        # self.manualControlSpeedW = message["manualControlSpeedW"]
        #logging.info("Vision update.")
        
        if True:
            pass
        else:
            with open('docs/robot.txt', 'a') as f:
                
                f.write(str(math.floor(message.robots_blue[0].x))+" "+str(math.floor(message.robots_blue[0].y))+" " + str((message.robots_blue[0].orientation))+(' \n'))
                
                #f.write("x[0]"+str(math.floor(message.robots_blue[0].x))+"cm\n\n")
                #f.write("y[0]"+str(math.floor(message.robots_blue[0].y))+"cm\n\n")
                #f.write("t[0]"+str(message.robots_blue[0].orientation)+"angulos\n\n")
                #time.sleep(6)
            
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