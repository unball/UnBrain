from .elements import *

class Field:
    def __init__(self, side):
        self.width = 1.75
        self.height = 1.35
        self.goalAreaWidth = 0.15
        self.goalAreaHeight = 0.70

        self.xmargin = 0.30
        self.ymargin = 0.18
        self.side = side

        self.areaEllipseSize = (0.35, 0.50)
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
    def __init__(self, n_robots=5, side=1, team_yellow=False, immediate_start=False, firasim=False, vssvision=False, debug=False, mirror=False, control=False):
        self._team = [TeamRobot(self, i, on=immediate_start) for i in range(n_robots)]
        self.enemies = [TeamRobot(self, i, on=immediate_start) for i in range(n_robots)]
        self.ball = Ball(self)
        self.field = Field(side)
        self.firasim = firasim
        self.vssvision = vssvision
        self.debug = debug
        self.mirror = mirror
        self.control =  control
        
        self.team_yellow = team_yellow

        self.allyGoals = 0
        self.enemyGoals = 0
        self.updateCount = 0

    # segue explicação abaixo
    def VSSVision_update(self, message):
        if self.debug:
            print("-------------------------")
            print("Executando com VSSVision:")
            if self.mirror: 
                print("UTILIZANDO CAMPO INVERTIDO")
            else:                   
                print("UTILIZANDO CAMPO SEM INVERSÃO")

        robot_id = 0
        # Reconhecemos a cor do time dos nossos robôs
        if self.team_yellow:
            yellow = self.team
            # blue = self.enemies
        else:
            # yellow = self.enemies
            blue = self.team
        
        
        if self.team_yellow:
            
            robot_id = 0
            # Faremos isso para a visão dos robôs amarelos, caso for do nosso time
            team = message.robots_yellow
            
            # Iteramos por cada robô
            for _ in team:

                if self.debug:
                    print(f"Yellow - {robot_id} | x {(message.robots_yellow[robot_id].x) / (1000):.2f} | y {(message.robots_yellow[robot_id].y) / (1000):.2f} | th {(message.robots_yellow[robot_id].orientation):.2f}")
                        
                #Atualizaremos as coordenadas do robô selecionado (robot_id)
                yellow[robot_id].update(
                    message.robots_yellow[robot_id].x / (1000),
                    message.robots_yellow[robot_id].y / (1000),
                    message.robots_yellow[robot_id].orientation
                )
                
                #passamos para o próximo robô
                robot_id += 1
                

        else:
            # O mesmo acima se aplica aqui, só que pra caso o nosso time seja o azul
            robot_id = 0

            team = message.robots_blue
    
            for _ in team:

                if self.debug:
                        print(f"Blue - {robot_id} | x {(message.robots_blue[robot_id].x) / (1000):.2f} | y {(message.robots_blue[robot_id].y) / (1000):.2f} | th {(message.robots_blue[robot_id].orientation):.2f}")
                        
                blue[robot_id].update(
                    message.robots_blue[robot_id].x / (1000),
                    message.robots_blue[robot_id].y / (1000),
                    message.robots_blue[robot_id].orientation
                    )
                    
                robot_id+=1
                #fim da função VSSVision_update

                    
        
    def FIRASim_update(self, message):
        # teamPos = zip(message["ally_x"], message["ally_y"], message["ally_th"], message["ally_vx"], message["ally_vy"], message["ally_w"])
        # enemiesPos = zip(message["enemy_x"], message["enemy_y"], message["enemy_th"], message["enemy_vx"], message["enemy_vy"], message["enemy_w"])
        if self.debug:
                print("-------------------------")
                print("Executando com firasim:")
                if self.mirror: 
                    print("UTILIZANDO CAMPO INVERTIDO")
                else:                   
                    print("UTILIZANDO CAMPO SEM INVERSÃO")

        if self.team_yellow: 
            yellow = self.team
        else:
            blue = self.team
            
        if self.team_yellow:
            for id, robot in enumerate(message.frame.robots_yellow):
                #yellow[robot_id].update(message.robots_yellow[robot_id].x,message.robots_yellow[robot_id].y, message.robots_yellow[robot_id].orientation)
                if self.debug:
                    print(f"Yellow - {id} | x {robot.x} | y {robot.y} | th {robot.orientation} | vx {robot.vx} | vy {robot.vy} | vorientation {robot.vorientation}")
                yellow[id].update_FIRASim(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)

        else:
            for id, robot in enumerate(message.frame.robots_blue):
                blue[id].update_FIRASim(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)
                if self.debug:
                    print(f"Blue - {id} | x {robot.x} | y {robot.y} | th {robot.orientation} | vx {robot.vx} | vy {robot.vy} | vorientation {robot.vorientation}")
                blue[id].update_FIRASim(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)

        # for robot, pos in zip(self.team, teamPos): robot.update(*pos)
        # for robot, pos in zip(self.enemies, enemiesPos): robot.update(*pos)
        #self.ball.update(message["ball_x"], message["ball_y"], message["ball_vx"], message["ball_vy"])
        self.ball.update_element_FIRASim(message.frame.ball.x, message.frame.ball.y, message.frame.ball.vx, message.frame.ball.vy)

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