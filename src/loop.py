from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy
from UVF_screen import UVFScreen
from communication.serialWifi import SerialRadio
from world import World

import threading

# Importa interface com FiraSim
from client import VSS

import robosim
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
from matplotlib.lines import Line2D
import numpy as np
import logging
import time
import sys
import signal
from vision.receiver import FiraClient
from client.client_pickle import ClientPickle
# from client.websocket import WebSocket


from strategy.automaticReplacer import AutomaticReplacer

import constants

class Loop:

    def __init__(self,
                loop_freq=60,
                draw_uvf=False,
                team_yellow=False,
                immediate_start=True,
                static_entities=False,
                referee=False,
                firasim=False,
                vssvision=False,
                mainvision=False,
                simulado=False,
                control=False,
                debug =False,
                port=5002,
                mirror=False, 
                n_robots=[0,1,2],
                
            ):
        
        self.loop_thread = None
        self.ws_thread = None
        self.threadScreen = None

        # Instancia interface com o simulador
        self.firasim = VSS(team_yellow=team_yellow)
        
        yellow_robots_pos = []
        blue_robots_pos = []
        field_type = 0  # 0 for Division B, 1 for Division A
        pos = [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]]
        if team_yellow:
            n_robots_yellow = len(n_robots)
            for i in n_robots:
                yellow_robots_pos += [pos[i]]
            n_robots_blue = 0 
        else:
            n_robots_blue = len(n_robots)
            for i in n_robots:
                blue_robots_pos += [pos[i]]
            n_robots_yellow = 0 
        time_step_ms = 16 # time step in milliseconds
        # ball initial position [x, y, v_x, v_y] in meters and meter/s
        ball_pos = [0.0, 0.3, 0.0, 0.0]

        # robots initial positions [[x, y, angle], [x, y, angle]...], where [[id_0], [id_1]...]
        # Units are meters and degrees
        
        self.simulado = robosim.VSS(
            field_type,
            n_robots_blue,
            n_robots_yellow,
            time_step_ms,
            ball_pos,
            blue_robots_pos,
            yellow_robots_pos,
        )

        # field_params = self.simulado.get_field_params()
        # print(f"estado do campo:{self.simulado.get_state()}")

        # Instancia de sinal caso haja interrupções no processo (ctrl + C)
        try: 
            signal.signal(signal.SIGINT, self.handle_SIGINT)
        except ValueError:
            print("tentou chamar signal fora da thread principal")
        # Instancia interfaces com o referee
        self.rc = RefereeCommands()
        self.rp = RefereePlacement(team_yellow=team_yellow)
        self.visionclient = FiraClient()
        # Instancia o mundo e a estratégia

        team_side = -1 if mirror else 1
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, referee=referee, firasim=firasim, vssvision=vssvision, mainvision=mainvision, simulado=simulado, control=control, debug=debug, mirror=mirror)
        
        self.arp = AutomaticReplacer(self.world)
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Variáveis
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)

        if self.world.mainvision:
            self.pclient = ClientPickle(port)

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        # if self.draw_uvf:
        #     self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            # self.UVF_screen.initialiazeScreen()
            # self.UVF_screen.initialiazeObjects()

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame):
        if self.world.firasim:
            for i, id in enumerate(self.world.n_robots):
                self.firasim.command.write(id, 0, 0)
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        elif self.world.vssvision:
            self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        elif self.world.mainvision:
            self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        elif self.world.simulado:
            self.simulado.step([(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        sys.exit(0) #OBS, já que se foi dado ctrl+c, o programa chamará essa função e qualquer coisa que acontecerá depois não ocorrerá por causa do sys.exit(0)

    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        # print("loop ALP:",(time.time()-self.t0)*1000)

        self.t0 = time.time()
        self.lastupdatecount = self.world.updateCount
        
        # Executa estratégia
        self.strategy.update(self.world)

        if self.world.vssvision: control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot is not None]
        if self.world.mainvision: control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot is not None]
        if self.world.firasim: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]
        if self.world.simulado: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]

        if self.world.debug and constants.DEBUG_ACTUATE:
            contador = 0
            for v1, v2 in control_output:
                if(self.world.firasim):
                    print(f"ACTUATE DO ROBO {contador} | V", v1, "| W", v2)
                else:
                    print(f"ACTUATE DO ROBO {contador} | V", v1, "| W", v2)
                contador+=1

        # Executa o controle
        if self.world.firasim:
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOn()
            for i, id in enumerate(self.world.n_robots):
                self.firasim.command.write(id, control_output[i][0], control_output[i][1])
        if self.world.vssvision:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.radio.send(self.world.n_robots, control_output)
        if self.world.mainvision:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.radio.send(self.world.n_robots, control_output)
        if self.world.simulado:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
            robos = control_output
            self.simulado.step(robos)
        
        if self.world.igglu:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
                
        # Desenha no ALP-GUI
        # self.draw()

    def busyLoop(self):

        if self.world.firasim:
            message = self.firasim.vision.read()
            #if message is not None: print("mensagem FIRASim", message)
            self.execute = True if message else False
            if self.execute: 
                self.world.FIRASim_update(message)

        if self.world.vssvision:
            # Inicia contagem do delay
            self.delay_camera = time.time()
            # Atribuimos a mensagem que queremos passar para a função VSSVision_update
            message = self.visionclient.receive_frame()
            self.execute = True if message else False
            if self.execute:
                self.world.VSSVision_update(message.detection)
        if self.world.mainvision:
            # Atribuimos a mensagem que queremos passar para a função update_main_vision
            message = self.pclient.receive()
            self.execute = message["running"]
            if message is not None: 
                self.world.update_main_vision(message)

        if self.world.simulado:
            message = self.simulado.get_state()
            self.execute = True if message else False
            if self.execute:
                self.world.update(message)
        
        elif((self.world.debug) and not (self.world.vssvision) and not (self.world.firasim) and not self.world.mainvision and not self.world.simulado):
            print("_________")
            print("Executando sem pacote:")
        

        if self.world.referee:
        
            command = self.rc.receive()
            
            if self.world.debug and command is not None:
                print(self.world.last_command)
                print(command)
            
            if command is not None:
                self.world.setLastCommand(command) 
                # obedece o comando e sai do busy loop
            else:
                self.strategy.manageReferee(self.arp, self.world.last_command)

    def draw(self):
        for robot in [r for r in self.world.team if r is not None]:
            clientProvider().drawRobot(robot.id, robot.x, robot.y, robot.th, robot.direction)

        for robot in self.world.enemies:
            clientProvider().drawRobot(robot.id+3, robot.x, robot.y, robot.th, 1, (0.6, 0.6, 0.6))

        clientProvider().drawBall(0, self.world.ball.x, self.world.ball.y)

    def websocket_thread(self):
        from client.websocket import WebSocket
        print("entrou no ws")
        webapp = WebSocket(loop=self)
        webapp.run()

    def run_loop(self):
        t0 = 0
        tempo_zero = time.time()

        logging.info("System is running")

        while self.running:
            
            # Executa o loop de visão e referee até dar o tempo de executar o resto
            self.busyLoop()
            while time.time() - t0 < self.loopTime:
                self.busyLoop()
            self.world.execTime = time.time() - t0
                
            # Tempo inicial do loop
            t0 = time.time()

            # Executa o loop
            self.loop()

            print(f"gfl{time.time()-tempo_zero:.2f}", end="\r", flush=True)

        logging.info("System stopped")

    def run(self):
        if self.ws_thread is None and self.loop_thread is None:
            # inicializa threads
            self.ws_thread = threading.Thread(target=self.websocket_thread)
            self.loop_thread = threading.Thread(target=self.run_loop)

            self.ws_thread.start()
            self.loop_thread.start() # inicia thread do loop

            robot_i=0
            field_dims=(170*4, 130*4)
            arrow_spaces=16

            x = np.arange(-field_dims[0]/2, field_dims[0]/2, arrow_spaces)
            y = np.arange(-field_dims[1]/2, field_dims[1]/2, arrow_spaces)
            X, Y = np.meshgrid(x, y)
            arrow_positions = np.array([X.flatten(), Y.flatten()]).T
            positions = []
            for i in range(arrow_positions.shape[0]):
                positions.append(arrow_positions[i]/400)

            if self.draw_uvf:
                plt.ion()
                plt.show(block=False)
                while self.running:
                    print(self.world.raw_team[0].field)
                    robot = self.world.raw_team[robot_i]
                    
                    angles = list(map(robot.field.F, positions))
                    
                    
                    pltuvf = plt.quiver(X, Y, np.cos(angles), np.sin(angles))
                    ax_static = plt.gca()
                    ax_dynamic = plt.gca()
                    mid = Circle((0, 0), radius=3, color='black', alpha=1, zorder=10)
                    ax_static.add_patch(mid)

                    marcas = [(-0.380*400,0.430*400),(0.380*400,0.430*400),(-0.380*400,-0.430*400),(0.380*400,-0.430*400)] #Marcas do campo
                    limites = [[(-300, -256), (-300, 256)], [(-300, 256), (300, 256)], [(300, -256), (300, 256)], [(-300, -256), (300, -256)]] #Linhas do campo
                    gol_amarelo = [[(340, -80), (340, 80)], [(300, -80), (300, 80)]] #Linhas do gol amarelo
                    gol_azul = [[(-340, -80), (-340, 80)], [(-300, -80), (-300, 80)]] #Linhas do gol azul
                    for pos in marcas:
                        plt.gca().add_patch(Circle(xy=pos,radius=4, color="black", alpha=1, zorder=10))
                    for pos in limites:
                        ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="grey", linewidth=2))
                    for pos in gol_amarelo:
                        if self.world.team_yellow:
                            ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="blue", linewidth=3))
                        else:
                            ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="yellow", linewidth=3))
                    for pos in gol_azul:
                        if self.world.team_yellow:
                            ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="yellow", linewidth=3))
                        else: 
                            ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="yellow", linewidth=3))
                    center_line = Line2D(*zip((0, -256), (0, 256)), color="gray", linewidth=1)
                    center_circle = Circle((0, 0), 80, facecolor='None', edgecolor='grey', linewidth=1, zorder=10)
                    ax_static.add_line(center_line)
                    ax_static.add_patch(center_circle)

                    robot_color = "yellow" if self.world.team_yellow else "blue"
                    robot_obj = Circle((robot.x*400, robot.y*400), 15, facecolor=robot_color, edgecolor= 'black', linewidth= 1.5, alpha=0.5, zorder=10)
                    robot_face = Arrow(robot.x*400, robot.y*400, np.cos(robot.th)*30, np.sin(robot.th)*30, width=25, facecolor=robot_color, alpha= 0.5, edgecolor= 'black', linewidth= 1)
                    ax_dynamic.add_patch(robot_obj)
                    ax_dynamic.add_patch(robot_face)

                    if not self.world.control:
                        bola = Circle(xy=(self.world.ball.x*400, self.world.ball.y*400),radius=7, color='tab:orange', alpha=1, zorder=10)
                        ax_dynamic.add_patch(bola)

                    plt.draw()
                    plt.pause(1/60)

                    pltuvf.remove()
                    ax_dynamic.remove()
                    del pltuvf
                    del ax_dynamic
                        
            # espera threads
            self.ws_thread.join()
            self.loop_thread.join()