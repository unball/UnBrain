from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy, Attacker, Defender, GoalKeeper
from UVF_screen import SystemTester
from communication.serialWifi import SerialRadio
from world import World

import threading

# Importa interface com FiraSim
from client import VSS

import random
import robosim

# matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm
from matplotlib.colors import LinearSegmentedColormap

import os
import gc
import numpy as np

# logging + filas (p/ suporte a threading)
import logging
import queue
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler
import copy

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
                draw_uvf=True,
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
                test_type="heatmap_team"
            ):
        
        self.loop_thread = None
        self.ws_thread = None
        self.threadScreen = None
        self.test_type = test_type

        self.team_yellow = team_yellow
        self.n_robots = n_robots
        self.referee = referee
        self.immediate_start = immediate_start
        self.control = control
        self.debug = debug
        self.mirror = mirror


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

        field_params = self.simulado.get_field_params()
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
        self.team_side = team_side
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, referee=referee, firasim=firasim, vssvision=vssvision, mainvision=mainvision, simulado=simulado, control=control, debug=debug, mirror=mirror)
        
        self.arp = AutomaticReplacer(self.world)
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Variáveis
        self.message = None
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)

        if self.world.mainvision:
            self.pclient = ClientPickle(port)

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        # if self.draw_uvf: # uso do UVFScreen legado
        #     self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            # self.UVF_screen.initialiazeScreen()
            # self.UVF_screen.initialiazeObjects()

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame, shutdown=True):
        '''
        Função que trata o sinal de interrupção (ctrl + C)
        ...
        Parâmetros
        ----------
        shutdown: bool
            Se True, o programa será encerrado
            Se False, o programa continuará rodando
        '''
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

        if shutdown:
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
            self.control_output = control_output
            robos = control_output
            self.simulado.step(robos)
        
        if self.world.igglu:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
                
        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):

        if self.world.firasim:
            message = self.firasim.vision.read()
            self.message = message if message else self.message
            #if self.message is not None: print("mensagem FIRASim", self.message)
            self.execute = True if self.message else False
            if self.execute: 
                self.world.FIRASim_update(self.message)

        if self.world.vssvision:
            # Inicia contagem do delay
            self.delay_camera = time.time()
            # Atribuimos a mensagem que queremos passar para a função VSSVision_update
            message = self.visionclient.receive_frame()
            self.message = message if message else self.message
            self.execute = True if self.message else False
            if self.execute:
                self.world.VSSVision_update(self.message.detection)
        if self.world.mainvision:
            # Atribuimos a mensagem que queremos passar para a função update_main_vision
            message = self.pclient.receive()
            self.message = message if message is not None else self.message
            self.execute = self.message["running"]
            if self.execute == False: # Se a visão parar de rodar, o robô para ao invés de continuar com o último comando
                self.handle_SIGINT(0,0, shutdown=False)
                
            elif self.message is not None: 
                self.world.update_main_vision(self.message)

        if self.world.simulado:
            message = self.simulado.get_state()
            self.message = message if message else self.message
            self.execute = True if self.message else False
            if self.execute:
                self.world.update(self.message)
        
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
                self.loop()
            self.world.execTime = time.time() - t0
                
            # Tempo inicial do loop
            t0 = time.time()

            # Executa o loop
            self.loop()

            print(f"gfl {time.time()-tempo_zero:.2f} FPS: {1/self.world.execTime}", end="\r", flush=True)

        logging.info("System stopped")

    def run(self):
        self.run_loop()

    def run_parallel(self, tester, thread_id, entity, duracao=300):
        logger = logging.getLogger(f"Thread-{thread_id}")

        t0 = 0
        tempo_zero = time.time()
        self.tempo_atual = time.time()-tempo_zero
        self.x_positions = []
        self.y_positions = []
        
        try:
            numeros, flag = tester.gera_randommatrix(a= -0.3, b= 0.3, size=13) # gera lista de 10 nums aleatorios

            field_type = 0 

            time_step_ms = 16

            last_ball_xs = []
            last_ball_ys = []

            # inicializa ambiente do simulado
            self.simulado = robosim.VSS(
                field_type,
                3,
                0,
                time_step_ms,
                [numeros[10], numeros[0], numeros[11], numeros[12]], # TODO: checar se bola tá de fato começando com alguma velocidade da bola diferente de 0
                [[-numeros[1], numeros[2], numeros[3]], 
                [-numeros[4], numeros[5], numeros[6]], 
                [-numeros[7], numeros[8], numeros[9]]],
                [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]],
            )

            ball_x, ball_y = self.simulado.get_state()[0], self.simulado.get_state()[1]
            
            logger.info("System is running")

            cronometro_5s, cronometro_1s = self.tempo_atual, self.tempo_atual
            last_reset_time = -1
            while self.tempo_atual < duracao:
                self.tempo_atual = time.time()-tempo_zero
                flag_1s, flag_5s = False, False
                numeros, flag = tester.gera_randommatrix(a= -0.3, b= 0.3, size=13)
                
                if self.tempo_atual - cronometro_5s > 5:
                    flag_5s = True
                    cronometro_5s = self.tempo_atual
                if self.tempo_atual - cronometro_1s > 1:
                    flag_1s = True
                    cronometro_1s = self.tempo_atual

                if flag_1s:
                    ball_x, ball_y = self.simulado.get_state()[0], self.simulado.get_state()[1]

                    last_ball_xs.insert(0, ball_x)
                    last_ball_ys.insert(0, ball_y)

                    if len(last_ball_xs) > 5 or len(last_ball_ys) > 5:
                        last_ball_xs.pop()
                        last_ball_ys.pop()

                if (int(self.tempo_atual != 0) and flag_5s) and (np.std(last_ball_xs) < 1e-4 and np.std(last_ball_ys) < 1e-4):
                    logger.info(f"BOLA PARADA: Reset na thread {thread_id}")

                    last_ball_xs, last_ball_ys = [], []

                    moving_ball_time = self.tempo_atual - last_reset_time - 5 if last_reset_time != -1 else self.tempo_atual - last_reset_time + 1 - 5
                    self.stuckball_register[thread_id].append(moving_ball_time)
                    
                    self.simulado.reset([numeros[10], numeros[0], numeros[11], numeros[12]],
                                        [[-numeros[1], numeros[2], numeros[3]], 
                                         [-numeros[4], numeros[5], numeros[6]], 
                                         [-numeros[7], numeros[8], numeros[9]]], 
                                         [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    last_reset_time =  self.tempo_atual

                if hasattr(self, 'simulado') and self.world.ball.x > 0.75:
                    try:
                        numeros, flag = tester.gera_randommatrix(a= -0.3, b= 0.3, size=13, timeout=1.0) if flag == False else numeros, True  # tenta gerar matriz mais rápido se tentativa anterior tiver dado timeout
                    except TimeoutError as e:
                        logger.error(f"Timeout: {str(e)}", exc_info=True)
                    except IndexError as e:
                        logger.error(f"Index: {numeros}")
                    except Exception as e:
                        logger.error(f"Erro na geração: {str(e)}", exc_info=True)
                    
                    logger.info(f"GOL na thread {thread_id}")

                    goal_interval = self.tempo_atual - last_reset_time if last_reset_time != -1 else self.tempo_atual - last_reset_time + 1
                    self.goal_register[thread_id].append(goal_interval)
                    # print(f"n_robots: {self.world.n_robots}")

                    self.simulado.reset([numeros[10], numeros[0], numeros[11], numeros[12]],
                                        [[-numeros[1], numeros[2], numeros[3]], 
                                         [-numeros[4], numeros[5], numeros[6]], 
                                         [-numeros[7], numeros[8], numeros[9]]], 
                                         [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    # self.simulado.reset([0.0, numeros[0], 0.0, 0.0], [[-numeros[1], numeros[2], numeros[3]], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]], [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    last_reset_time = self.tempo_atual


                self.busyLoop()
                while time.time() - t0 < self.loopTime:
                    self.busyLoop()
                    self.loop()
                self.world.execTime = time.time() - t0
                    
                t0 = time.time()
                self.loop()

                # atualiza listas de posições
                self.team_positions = [(round(robot.x, 3), round(robot.y, 3)) 
                                    for robot in self.world.raw_team]
                
                for robot in self.world.raw_team:
                    if (entity == None and (self.test_type != "heatmap_ball")) or (entity != None and (isinstance(robot.entity, entity))):
                        self.x_positions.append(round(robot.x, 3))
                        self.y_positions.append(round(robot.y, 3))
                    elif (self.test_type == "heatmap_ball"):
                        self.x_positions.append(round(ball_x, 3))
                        self.y_positions.append(round(ball_y, 3))

                self.all_positions[thread_id] = self.team_positions
                self.positions_record.append([round(time.time()-tempo_zero, 2), 
                                            self.all_positions])
                
                # logger otimizado (uma vez p segundo)
                if flag_1s:
                    logger.debug(f"gfl {round(time.time()-tempo_zero, 2)} {self.all_positions}")

        finally:
            self.runningtime_register.append(self.tempo_atual)
            logger.info(f"System stopped, position list size: {len(self.x_positions)}")

    def test(self, n_threads=20):
            # inicializa testador
            tester = SystemTester(self.world)
            self.thread_envs = [[] for _ in range(n_threads)] # separação em threads para uso futuro, favor não desfazer isso
            self.all_positions = copy.deepcopy(self.thread_envs)
            self.goal_register = copy.deepcopy(self.thread_envs)
            self.stuckball_register = copy.deepcopy(self.thread_envs)
            self.runningtime_register = []
            self.positions_record = []
            # print(len(self.all_positions))

            if self.draw_uvf:
                # cria thread do loop, importante pois mesmo as threads não interagindo bem com o matplotlib isso permite que o loop rode normalmente.
                self.loop_thread = threading.Thread(target=self.run_loop) 
                self.loop_thread.start()

                # O parâmetro render_uvf=True desacelera o render do matplotlib, esteja ciente disso ao habilitar
                # Quanto mais setas no render do uvf, mais lento fica o render. Aumentar a quantidade de setas sem diminuir a loop_freq *não vai adiantar*, o render vai ficar lento.
                tester.run_singletest(loop=self, robot_i=0, render_uvf=False)

                self.loop_thread.join()
            else:
                loop_list = []
                teams = []
                for i in range(n_threads):
                    # cria threads
                    if self.test_type == "heatmap_attacker":
                        loop_thread = threading.Thread(target=self.run_parallel, args=(tester, i, Attacker), daemon=True)
                    elif self.test_type == "heatmap_defender":
                        loop_thread = threading.Thread(target=self.run_parallel, args=(tester, i, Defender), daemon=True)
                    elif self.test_type == "heatmap_goalkeeper":
                        loop_thread = threading.Thread(target=self.run_parallel, args=(tester, i, GoalKeeper), daemon=True)
                    else:
                        loop_thread = threading.Thread(target=self.run_parallel, args=(tester, i, None), daemon=True)
                    teams.append(self.world.raw_team)
                    loop_thread.start() # inicia essa thread do loop
                    loop_list.append(loop_thread)

                for thread in loop_list:
                    thread.join()

                tester.gera_heatmap(self.x_positions, self.y_positions)

                # cria dicionário de registros de dados da simulação
                register_dict = {"runningtime": self.runningtime_register,
                                 "goalcount": self.goal_register,
                                 "stuckball": self.stuckball_register}
                
                data_dict = tester.gera_datadict(register_dict)

                # print mais bonitinho dos dados
                for key, value in data_dict.items():
                    print(f"{key}: {value}")

                plt.show()
