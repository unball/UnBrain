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

from gi.repository import GLib
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

#MainVision
from vision.receiver import FiraClient
from client.client_pickle import ClientPickle
from MainVision.helpers import Mux
from MainVision.controller.states import DummyState
# from client.websocket import WebSocket


from strategy.automaticReplacer import AutomaticReplacer

import constants

class Loop:

    def __init__(self,
                loop_freq=120,
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
        self.execute = True
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

        #MainVision
        self.communicationSystems = Mux([SerialRadio(self.world)])    
        self.__events = queue.Queue()
        """Eventos agendados. Essa fila é útil para que a view agende eventos a serem executados no momento oportuno pelo backend, evitando condições de corrida."""
        self.__quitRequested = False
        """Flag que indica se o loop do backend deve terminar"""
        
        # Variáveis
        self.message = None
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)

        self.port = port
        self.pclient = None

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

    def initialize_pickle(self):
        self.pclient = ClientPickle(self.port)
        print("Client Inicializado.")


    def stop(self):
        """Faz a flag `__quitRequested` ser `True`, o que provocará a parada de `loop` na thread de controller."""
        self.execute = False
        print("oiiiii")
        self.running = False
        self.handle_SIGINT(0,0, shutdown=False)
        
    def unsetState(self):
        """Define que o estado a ser executado no `loop` é um estado que não faz nada."""
        self.__state = DummyState(self)
   
    def setState(self, state):
        """Define o estado que será executado no `loop`"""
        self.__state = state

    def addEvent(self, method, *args, run_when_done_with_glib=None):
        """Agrega um evento para execução posterior no próximo loop."""
        self.__events.put({
            "method": method,
            "args": args,
            "glib_run": run_when_done_with_glib
        })

    def runQueuedEvents(self):
        """Despacha todos os eventos pendentes."""
        while not self.__events.empty():
            try:
                ev = self.__events.get_nowait()
                ev["method"](*ev["args"])
                if ev["glib_run"] is not None:
                    # se vier com callback para GLib, agenda no thread principal de GUI
                    GLib.idle_add(ev["glib_run"][0], *ev["glib_run"][1:])
            except Exception as e:
                print(f"[World] falha ao rodar evento: {e}")

    def setRunning(self, state):
        """Recebe uma flag `state` indicando se o jogo está ou não rodando."""
        self.running = state
        if state is True:
            for robot in self.world.robots:
                robot.lastTimeAlive = time.time()
                robot.spin = 0

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
            message = self.pclient.receive() if self.pclient else None
            self.message = message if message else self.message
            if self.message:
                self.execute = self.message["running"]
            if self.execute == False: # Se a visão parar de rodar, o robô para ao invés de continuar com o último comando
                self.handle_SIGINT(0,0, shutdown=False)
            elif self.message is not None:
                self.world.update_main_vision(self.message)
                # roda aqui todos os eventos que foram agendados no mundo

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

            print(f"gfl {time.time()-tempo_zero:.2f}, FPS {1/self.world.execTime:.2f}", end="\r", flush=True)

        logging.info("System stopped")

    def run(self):
        self.run_loop()

