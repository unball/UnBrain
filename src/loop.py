from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy
from UVF_screen import UVFScreen
from communication.serialWifi import SerialRadio
from world import World

# Importa interface com FiraSim
from client import VSS

import matplotlib.pyplot as plt
import numpy as np
import logging
import time
import sys
import signal
from vision.receiver import FiraClient

from strategy.automaticReplacer import AutomaticReplacer

import constants

class Loop:

    def __init__(self,
                loop_freq=90,
                draw_uvf=False,
                team_yellow=False,
                immediate_start=False,
                static_entities=False,
                referee=False,
                firasim=False,
                vssvision=False,
                control=False,
                debug =False,
                mirror=False, 
                n_robots=[0,1,2]
            ):
        # Instancia interface com o simulador
        self.firasim = VSS(team_yellow=team_yellow)

        # Instancia de sinal caso haja interrupções no processo (ctrl + C)
        signal.signal(signal.SIGINT, self.handle_SIGINT)

        # Instancia interfaces com o referee
        self.rc = RefereeCommands()
        self.rp = RefereePlacement(team_yellow=team_yellow)
        self.visionclient = FiraClient()
        # Instancia o mundo e a estratégia

        team_side = -1 if mirror else 1
        
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start,referee=referee, firasim=firasim, vssvision=vssvision, control=control, debug=debug, mirror=mirror)
        
        self.arp = AutomaticReplacer(self.world)
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Variáveis
        self.t0 = time.time()
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.radio = SerialRadio(control = control, debug = self.world.debug)
        self.delay_camera = 0

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        if self.draw_uvf:
            self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            self.UVF_screen.initialiazeScreen()
            self.UVF_screen.initialiazeObjects()

    # Função do sinal de interrupção (faz com que pare o robô imediatamente, (0,0) )
    def handle_SIGINT(self, signum, frame):
        if self.world.firasim:
            for i, id in enumerate(self.world.n_robots):
                print (i, id)
                self.firasim.command.write(id, 0, 0)
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOff()
        elif self.world.vssvision:
            self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
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
        if self.world.firasim: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]

        if self.world.debug and constants.DEBUG_ACTUATE:
            contador = 0
            for vr, vl in control_output:
                print(f"ACTUATE DO ROBO {contador} | VR", vl, "| VL", vr)
                contador+=1

        # Executa o controle
        if self.world.firasim:
            for robot in self.world.raw_team: 
                if robot is not None: robot.turnOn()
            for i, id in enumerate(self.world.n_robots):
                print (i, id)
                self.firasim.command.write(id, control_output[i][0], control_output[i][1])
        if self.world.vssvision:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.radio.send(self.world.n_robots, control_output)

        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):

        if(self.world.firasim):
            message = self.firasim.vision.read()
            #if message is not None: print("mensagem FIRASim", message)
            self.execute = True if message else False
            if self.execute: 
                self.world.FIRASim_update(message)

        if(self.world.vssvision):
            
            # Inicia contagem do delay
            self.delay_camera = time.time()
            # Atribuimos a mensagem que queremos passar para a função VSSVision_update
            message = self.visionclient.receive_frame()
            self.execute = True if message else False
            if self.execute:
                self.world.VSSVision_update(message.detection)

                # Finaliza contagem do delay
                self.delay_camera -= time.time()
                print("------------------------------------------------\n")
                print(f'Delay da camera: {self.delay_camera} segundos\n')
                print("------------------------------------------------\n")

        
        elif((self.world.debug) and not (self.world.vssvision) and not (self.world.firasim)):
            print("_________________________")
            print("Executando sem pacote:")
        if self.world.referee:
        
            command = self.rc.receive()
            
            if self.world.debug and command is not None:
                print(self.world.last_command)
                print(command)
            elif self.world.debug and command is None:
                print("NENHUM PACOTE RECEBIDO AINDA")
            
            if command is not None:
                self.world.setLastCommand(command) 
                # obedece o comando e sai do busy loop
            else:
                self.strategy.manageReferee(self.arp, self.world.last_command)
           
    def draw(self):
        for robot in [r for r in self.world.team if r is not None]:
            clientProvider().drawRobot(robot.id, robot.x, robot.y, robot.thvec_raw.vec[0], robot.direction)

        for robot in self.world.enemies:
            clientProvider().drawRobot(robot.id+3, robot.x, robot.y, robot.thvec_raw.vec[0], 1, (0.6, 0.6, 0.6))

        clientProvider().drawBall(0, self.world.ball.x, self.world.ball.y)

    def run(self):
        t0 = 0

        logging.info("System is running")

        while self.running:
            
            # Executa o loop de visão e referee até dar o tempo de executar o resto
            self.busyLoop()
            while time.time() - t0 < self.loopTime:
                self.busyLoop()
                
            # Tempo inicial do loop
            t0 = time.time()

            # Executa o loop
            self.loop()

            if self.draw_uvf:
                self.UVF_screen.updateScreen()

        logging.info("System stopped")