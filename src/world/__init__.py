from .elements import *
from tools import RangeKutta
class Field:
    def __init__(self, side):
        self.width = 1.67
        self.height = 1.23
        self.goalAreaWidth = 0.15
        self.goalAreaHeight = 0.7

        self.xmargin =  0.10
        self.ymargin = 0.20
        self.side = side

        self.goalDepth = 0.1

        self.areaEllipseSize = (0.27, 0.45)
        self.areaEllipseCenter = (-self.maxX + 0.07, 0)

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
    def allyGoalPos(self):
        return np.array([-self.maxX, 0])
   
    @property
    def goalAreaSize(self):
        return (self.goalAreaWidth, self.goalAreaHeight)

class World:
    def __init__(self, n_robots=[0,1,2], side=1, team_yellow=False, immediate_start=False, referee=False, firasim=False, vssvision=False, mainvision=False, simulado=False, debug=False, mirror=False, control=False, last_command=None):
        self.n_robots = n_robots
        self._team = [None,None,None]
        for i in self.n_robots:
            self._team[i] = TeamRobot(self, i, on=immediate_start)
        self.enemies = [TeamRobot(self, i, on=immediate_start) for i in self.n_robots]
        for robot in self.enemies:
            if robot is not None:
                robot.xvec.add(1000000000000000)
        self.ball = Ball(self)
        self.field = Field(side)
        self.referee = referee
        self.firasim = firasim
        self.vssvision = vssvision
        self.mainvision = mainvision
        self.simulado = simulado
        self.debug = debug
        self.mirror = mirror
        self.control =  control
        self.last_command = last_command
        self._referenceTime = 0
        self.dt = 0
        self.marginPos = self.field.marginPos
        self.allyGoalPos = self.field.allyGoalPos
        self.goalAreaSize = self.field.goalAreaSize
        self.delay_camera = 0
        self.t0 = time.time()
        self.execTime = 0

        
        self.team_yellow = team_yellow

        self.allyGoals = 0
        self.enemyGoals = 0
        self.updateCount = 0

    def update_main_vision(self, message):
        if self.team_yellow: 
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        robot_id = 0
        for robot in range(message["n_robots"]):
            if self.team_yellow: 
                yellow[robot_id].update(
                    message["robots"][robot_id]["pos_x"], 
                    message["robots"][robot_id]["pos_y"], 
                    message["robots"][robot_id]["th"], 
                    message["robots"][robot_id]["vel_x"], 
                    message["robots"][robot_id]["vel_y"], 
                    message["robots"][robot_id]["w"]
                )
            else:
                blue[robot_id].update(
                    message["robots"][robot_id]["pos_x"], 
                    message["robots"][robot_id]["pos_y"], 
                    message["robots"][robot_id]["th"], 
                    message["robots"][robot_id]["vel_x"], 
                    message["robots"][robot_id]["vel_y"], 
                    message["robots"][robot_id]["w"]
                )
            robot_id+=1
       
        self.ball.update_element(message["ball"]["pos_x"], message["ball"]["pos_y"], message["ball"]["vel_x"], message["ball"]["vel_y"])
        self.checkBatteries = message["check_batteries"]
        self.manualControlSpeedV = message["manualControlSpeedV"]
        self.manualControlSpeedW = message["manualControlSpeedW"]

        self.updateCount += 1
     
    def update(self, message):
        if self.team_yellow: 
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        self.dt = time.time() - self._referenceTime
        robot_id = 0
        for robot in self.n_robots:
            if self.team_yellow:
                yellow[robot].raw_update(
                    message[5+(6*robot)], 
                    message[6+(6*robot)], 
                    message[7+(6*robot)]*np.pi/180
                )
                
                yellow[robot].calc_velocities(self.dt)

            else:
                print(message[7+(6*robot_id)]*np.pi/180)
                blue[robot].raw_update(
                    message[5+(6*robot)], 
                    message[6+(6*robot)], 
                    message[7+(6*robot)]*np.pi/180
                )

                blue[robot].calc_velocities(self.dt)
            robot_id+=1
        self.ball.raw_update(message[0], message[1])
        
        self.ball.calc_velocities(self.dt)
        self.dt = time.time() - self._referenceTime
        self._referenceTime = time.time()
        self.updateCount += 1





    # segue explicação abaixo
    def VSSVision_update(self, message):
        if self.debug:
            print("-------------------------")
            print("Executando com VSSVision:")
            if not self.mirror and self.team_yellow or self.mirror and not self.team_yellow: 
                print("UTILIZANDO CAMPO INVERTIDO")
            else:                   
                print("UTILIZANDO CAMPO SEM INVERSÃO")

        # Reconhecemos a cor do time dos nossos robôs
        if self.team_yellow:
            yellow = self.team
        else:
            blue = self.team
        
        
        if self.team_yellow:
            self.dt = time.time() - self._referenceTime
            # Faremos isso para a visão dos robôs amarelos, caso for do nosso time
            # Iteramos por cada robô
            for i, robot in enumerate(message.robots_yellow):
                if i < len(self.n_robots):
                    if self.debug:
                        print(f"Yellow - {self.n_robots[i]} | x {(robot.x) / (1000):.2f} | y {(robot.y) / (1000):.2f} | th {(robot.orientation):.2f}")
                            
                    #Atualizaremos as coordenadas do robô selecionado (robot_id)
                    yellow[self.n_robots[i]].raw_update(
                        robot.x / (1000),
                        robot.y / (1000),
                        robot.orientation
                    )
                    yellow[self.n_robots[i]].calc_velocities(self.dt)
                

        else:
            self.dt = time.time() - self._referenceTime
            # O mesmo acima se aplica aqui, só que pra caso o nosso time seja o azul
    
            for i, robot in enumerate(message.robots_blue):
                if i < len(self.n_robots):
                    if self.debug:
                        print(f"Blue - {self.n_robots[i]} | x {(robot.x) / (1000):.2f} | y {(robot.y) / (1000):.2f} | th {(robot.orientation):.2f}")
                    blue[self.n_robots[i]].raw_update(
                        robot.x / (1000),
                        robot.y / (1000),
                        robot.orientation
                        )
                    blue[self.n_robots[i]].calc_velocities(self.dt)
                    #fim da função VSSVision_update
        self.ball.raw_update((message.balls[0].x) /1000, (message.balls[0].y) / 1000)
        if self.debug:
            print(f"BALL {(message.balls[0].x/1000):.2f} {(message.balls[0].y / 1000):.2f}")
        self.ball.calc_velocities(self.dt)

        #Cálculo delay Cam
        self.delay_camera = time.time() - self.delay_camera
        print(f'Delay da camera: {self.delay_camera} segundos', end='\r', flush=True)
        if self.delay_camera > 0.09:
            for robot in self.raw_team:
                if robot is not None:
                    rr = np.array(robot.pos)
                    vr = np.array(robot.v)
                    w = robot.w
                    th = robot.th
                    print(time.time() - self.t0)
                    delta_t = self.delay_camera
                    T = self.execTime
                    
                    new_pose = RangeKutta(rr,vr,th,T,delta_t,w)
                    robot.raw_update(self.field.side * new_pose[0],new_pose[1],new_pose[2])
                    robot.calc_velocities(delta_t)
            rb = np.array(self.ball.pos)
            vb = np.array(self.ball.v)
            new_pose = RangeKutta(rb,vb,th,T,delta_t)
            self.ball.raw_update(self.field.side * new_pose[0],new_pose[1])
            self.ball.calc_velocities(delta_t)



        self.delay_camera = time.time()
        self._referenceTime = time.time()
        self.updateCount += 1
        

                    
        
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
            for i, robot in enumerate(message.frame.robots_yellow):
                if i < len(self.n_robots):
                    #yellow[robot_id].update(message.robots_yellow[robot_id].x,message.robots_yellow[robot_id].y, message.robots_yellow[robot_id].orientation)
                    if self.debug:
                        print(f"Yellow - {self.n_robots[i]} | x {robot.x:.2f} | y {robot.y:.2f} | th {robot.orientation:.2f} | vx {robot.vx:.2f} | vy {robot.vy:.2f} | vorientation {robot.vorientation:.2f}")
                    yellow[self.n_robots[i]].update_FIRASim(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)
                    
        else:
            for i, robot in enumerate(message.frame.robots_blue):
                if i < len(self.n_robots):
                    if self.debug:
                        print(f"Blue - {self.n_robots[i]} | x {robot.x:.2f} | y {robot.y:.2f} | th {robot.orientation:.2f} | vx {robot.vx:.2f} | vy {robot.vy:.2f} | vorientation {robot.vorientation:.2f}")
                    blue[self.n_robots[i]].update_FIRASim(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)


        # for robot, pos in zip(self.team, teamPos): robot.update(*pos)
        # for robot, pos in zip(self.enemies, enemiesPos): robot.update(*pos)
        #self.ball.update(message["ball_x"], message["ball_y"], message["ball_vx"], message["ball_vy"])
        if self.debug:
            print(f"BALL | x {(message.frame.ball.x):.2f} | y {(message.frame.ball.y):.2f}")
        self.ball.update_element(message.frame.ball.x, message.frame.ball.y, message.frame.ball.vx, message.frame.ball.vy)

        self.updateCount += 1

    def setLastCommand(self, last_command):
        self.last_command = last_command

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