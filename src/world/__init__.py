from .elements import *
from tools import RangeKutta
from strategy import AI_Attacker
class Field:
    def __init__(self, side):
        self.width = 1.50
        self.height = 1.30
        self.goalAreaWidth = 0.15
        self.goalAreaHeight = 0.40
        self.penaltyAreaWidth = 0.70
        self.penaltyAreaDepth = 0.15

        self.xmargin = 0.003
        self.ymargin = 0.003
        self.side = side

        self.goalDepth = 0.1

        self.areaEllipseSize = (0.15, 0.45)
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
        return self.maxX
    
    @property
    def marginY(self):
        return self.maxY

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

    def insideGoalNet(self, pos):
        """
        Retorna se a posição (x, y) está dentro da rede de algum dos gols.
        Aplica uma margem de segurança extra de 5cm para compensar o raio da bola 
        nas simulações físicas (TraveSim/FiraSim).
        """
        x, y = pos
        goal_half_width = (self.goalAreaHeight / 2)
        
        if x > self.maxX and abs(y) < goal_half_width:
            return "ally_goal"
        elif x < -self.maxX and abs(y) < goal_half_width:
            return "enemy_goal"
        
        return None

class World:
    def __init__(self, n_robots=[0,1,2], side=1, team_yellow=False, immediate_start=False, referee=False, firasim=False, travesim=False, rsim=False, simulado=False, mainsystem=False, debug=False, mirror=False, control=False, AI_attacker=False, enemy_AI=False, last_command=None, teleport_mode=None, flag_use_kalman=False, flag_use_neural_estimator=False):
        self.flag_use_kalman = flag_use_kalman
        self.flag_use_neural_estimator = flag_use_neural_estimator
        print(f"DEBUG: flag_use_kalman set to {self.flag_use_kalman}, flag_use_neural_estimator set to {self.flag_use_neural_estimator}")
        self.n_robots = n_robots
        self._team = [None,None,None]
        self.enemies = [None,None,None]
        for i in self.n_robots:
            self._team[i] = TeamRobot(self, i, on=immediate_start)
            self.enemies[i] = TeamRobot(self, i, on=immediate_start)
        for robot in self.enemies:
            if robot is not None:
                robot.xvec.add(1000000000000000)
        self.ball = Ball(self)
        self.field = Field(side)
        self.referee = referee
        self.firasim = firasim
        self.travesim = travesim
        self.rsim = rsim
        self.simulado = simulado
        self.mainsystem = mainsystem
        self.debug = debug
        self.mirror = mirror
        self.control =  control
        self.AI_attacker = AI_attacker
        self.enemy_AI = enemy_AI
        self.mode = None
        if self.firasim: self.mode = "firasim"
        elif self.travesim: self.mode = "travesim"
        elif self.rsim: self.mode = "rsim"
        elif self.simulado: self.mode = "simulado"
        elif self.mainsystem: self.mode = "fisico"
        self.last_command = last_command
        self.teleport_mode = teleport_mode
        self._referenceTime = 0
        self.dt = 0
        self.marginPos = self.field.marginPos
        self.allyGoalPos = self.field.allyGoalPos
        self.goalAreaSize = self.field.goalAreaSize
        self.delay_camera = 0
        self.t0 = time.time()
        self.execTime = 0
        self.igglu = True
        
        self.team_yellow = team_yellow

        self.teleport_config = {}
        if self.teleport_mode is not None:
            import json
            import os
            try:
                with open("src/teleport_config.json", "r") as f:
                    self.teleport_config = json.load(f)
            except Exception as e:
                print(f"[WORLD] Erro ao carregar teleport_config.json: {e}")

        self.allyGoals = 0
        self.enemyGoals = 0
        self.updateCount = 0
        if self.AI_attacker:
            robot = self.team[self.n_robots[0]]
            robot.updateEntity(AI_Attacker)
            robot.entity._control.output(robot)

    def update_main_vision(self, message):
        if self.team_yellow: 
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        robot_id = 0
        for robot in self.n_robots:
            if self.team_yellow: 
                yellow[robot].update(
                    message["robots"][robot]["pos_x"], 
                    message["robots"][robot]["pos_y"], 
                    message["robots"][robot]["th"], 
                    message["robots"][robot]["vel_x"], 
                    message["robots"][robot]["vel_y"], 
                    message["robots"][robot]["w"],
                    message["robots"][robot].get("raw_x", message["robots"][robot]["pos_x"]),
                    message["robots"][robot].get("raw_y", message["robots"][robot]["pos_y"]),
                    message["robots"][robot].get("raw_th", message["robots"][robot]["th"])
                )
            else:
                blue[robot].update(
                    message["robots"][robot]["pos_x"],
                    message["robots"][robot]["pos_y"],
                    message["robots"][robot]["th"],
                    message["robots"][robot]["vel_x"],
                    message["robots"][robot]["vel_y"],
                    message["robots"][robot]["w"],
                    message["robots"][robot].get("raw_x", message["robots"][robot]["pos_x"]),
                    message["robots"][robot].get("raw_y", message["robots"][robot]["pos_y"]),
                    message["robots"][robot].get("raw_th", message["robots"][robot]["th"])
                )
            robot_id+=1
        
        self.ball.update_element(
            message["ball"]["pos_x"], 
            message["ball"]["pos_y"], 
            message["ball"]["vel_x"], 
            message["ball"]["vel_y"],
            0,
            message["ball"].get("raw_x", message["ball"]["pos_x"]),
            message["ball"].get("raw_y", message["ball"]["pos_y"])
        )
        self.checkBatteries = message["check_batteries"]
        self.manualControlSpeedV = message["manualControlSpeedV"]
        self.manualControlSpeedW = message["manualControlSpeedW"]

        self.updateCount += 1

    def update_from_rsoccer(self, message):
        """Atualiza a renderização com base nos estados do rsoccer passados do AI worker"""
        bx = message['ball'].get('x', 0)
        by = message['ball'].get('y', 0)
        bvx = message['ball'].get('vx', 0)
        bvy = message['ball'].get('vy', 0)
        
        self.ball.update_element(bx, by, bvx, bvy)

        if self.team_yellow:
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        for r_dict in message.get('robots_yellow', []):
            r_id = r_dict['id']
            if r_id < len(yellow):
                yellow[r_id].update_element(r_dict['x'], r_dict['y'], r_dict['vx'], r_dict['vy'], r_dict['vtheta'], r_dict['x'], r_dict['y'], r_dict['theta'])

        for r_dict in message.get('robots_blue', []):
            r_id = r_dict['id']
            if r_id < len(blue):
                blue[r_id].update_element(r_dict['x'], r_dict['y'], r_dict['vx'], r_dict['vy'], r_dict['vtheta'], r_dict['x'], r_dict['y'], r_dict['theta'])
                
        self.updateCount += 1
     
    def update(self, message):
        if self.team_yellow:
            yellow = self.team
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        self.dt = time.time() - self._referenceTime
        # Velocidade no rsim: o passo de física avança rsim_time_step_ms (dt
        # SIMULADO, fixo) por step, então estimar v = Δpos/dt com o dt de relógio
        # escala a velocidade por (dt_sim/dt_real) e a torna dependente do fps do
        # loop (ex.: a 200fps a velocidade fica ~5x inflada). Usamos o dt simulado.
        dt_sim = getattr(self, 'rsim_dt_s', 0.016)
        # n_enemy: número de inimigos no rsim (azuis antes dos amarelos no array).
        # Com n_enemy=3, aliados amarelos ficam deslocados por 6*3=18 posições.
        n_enemy = getattr(self, 'rsim_n_enemies', 0)
        # robot_idx é o índice sequencial no array do rsim (0, 1, 2...)
        # robot é o ID real do robô no time (pode ser 0, 1 ou 2, em qualquer ordem)
        for robot_idx, robot in enumerate(self.n_robots):
            if self.team_yellow:
                # amarelos vêm após os n_enemy azuis no estado flat
                offset = 5 + 6*n_enemy + 6*robot_idx
                yellow[robot].raw_update(
                    message[offset],
                    message[offset+1],
                    np.deg2rad(message[offset+2])
                )
                yellow[robot].calc_velocities(dt_sim)
            else:
                # azuis vêm primeiro (sem mudança)
                offset = 5 + 6*robot_idx
                blue[robot].raw_update(
                    message[offset],
                    message[offset+1],
                    np.deg2rad(message[offset+2])
                )
                blue[robot].calc_velocities(dt_sim)
                if self.debug:
                    print(f"Blue - {robot} | x {message[offset]:.2f} | y {message[offset+1]:.2f} | th {message[offset+2]:.2f}")

        # Atualiza posições dos inimigos a partir do estado rsim (para observação e UI)
        n_ally = len(self.n_robots)
        for i in range(n_enemy):
            if self.team_yellow:
                enemy_offset = 5 + 6*i          # inimigos são azuis, vêm primeiro
            else:
                enemy_offset = 5 + 6*n_ally + 6*i  # inimigos são amarelos, vêm depois
            if i < len(self.enemies) and self.enemies[i] is not None:
                self.enemies[i].raw_update(message[enemy_offset], message[enemy_offset+1], np.deg2rad(message[enemy_offset+2]))
                self.enemies[i].calc_velocities(dt_sim)

        self.ball.raw_update(message[0], message[1])
        self.ball.calc_velocities(dt_sim)
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
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team
        
        self.dt = time.time() - self._referenceTime
        
        # Faremos isso para a visão dos robôs amarelos
        for i, robot in enumerate(message.robots_yellow):
            robot_id = getattr(robot, 'robot_id', i)
            if robot_id < 3 and yellow[robot_id] is not None:
                if self.debug:
                    print(f"Yellow - {robot_id} | x {(robot.x) / (1000):.2f} | y {(robot.y) / (1000):.2f} | th {(robot.orientation):.2f}")
                        
                yellow[robot_id].raw_update(
                    robot.x / (1000),
                    robot.y / (1000),
                    robot.orientation
                )
                yellow[robot_id].calc_velocities(self.dt)

        # E para os azuis
        for i, robot in enumerate(message.robots_blue):
            robot_id = getattr(robot, 'robot_id', i)
            if robot_id < 3 and blue[robot_id] is not None:
                if self.debug:
                    print(f"Blue - {robot_id} | x {(robot.x) / (1000):.2f} | y {(robot.y) / (1000):.2f} | th {(robot.orientation):.2f}")
                
                blue[robot_id].raw_update(
                    robot.x / (1000),
                    robot.y / (1000),
                    robot.orientation
                    )
                blue[robot_id].calc_velocities(self.dt)
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
                    robot.raw_update(new_pose[0],new_pose[1],new_pose[2])
                    robot.calc_velocities(delta_t)
            rb = np.array(self.ball.pos)
            vb = np.array(self.ball.v)
            new_pose = RangeKutta(rb,vb,th,T,delta_t)
            self.ball.raw_update(new_pose[0],new_pose[1])
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
            blue = self.enemies
        else:
            yellow = self.enemies
            blue = self.team

        if self.flag_use_kalman:
            if hasattr(message, 'step') and message.step > 0:
                if not hasattr(self, 'last_step'):
                    self.last_step = message.step
                    self.dt = 0.016
                else:
                    if self.travesim:
                        self.dt = (message.step - self.last_step) / 1000.0 # TraveSim ms
                    else:
                        self.dt = (message.step - self.last_step) * (1.0 / 60.0) # FiraSim frames
                    self.last_step = message.step
            else:
                self.dt = time.time() - self._referenceTime
            if self.dt <= 0:
                self.dt = 0.016 # Fallback protection against division by zero
        else:
            self.dt = time.time() - self._referenceTime
            
        for i, robot in enumerate(message.frame.robots_yellow):
            if i < 3 and yellow[i] is not None:
                if self.debug:
                    print(f"Yellow - {i} | x {robot.x:.2f} | y {robot.y:.2f} | th {robot.orientation:.2f} | vx {robot.vx:.2f} | vy {robot.vy:.2f} | vorientation {robot.vorientation:.2f}")
                yellow[i].updateSimu(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)
                
        for i, robot in enumerate(message.frame.robots_blue):
            if i < 3 and blue[i] is not None:
                if self.debug:
                    print(f"Blue - {i} | x {robot.x:.2f} | y {robot.y:.2f} | th {robot.orientation:.2f} | vx {robot.vx:.2f} | vy {robot.vy:.2f} | vorientation {robot.vorientation:.2f}")
                blue[i].updateSimu(robot.x, robot.y, robot.orientation, robot.vx, robot.vy, robot.vorientation)


        # for robot, pos in zip(self.team, teamPos): robot.update(*pos)
        # for robot, pos in zip(self.enemies, enemiesPos): robot.update(*pos)
        #self.ball.update(message["ball_x"], message["ball_y"], message["ball_vx"], message["ball_vy"])
        if self.debug:
            print(f"BALL | x {(message.frame.ball.x):.2f} | y {(message.frame.ball.y):.2f}")
        self.ball.update_element(message.frame.ball.x, message.frame.ball.y, message.frame.ball.vx, message.frame.ball.vy)

        self._referenceTime = time.time()
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