from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy
from UVF_screen import UVFScreen
from communication.serialWifi import SerialRadio
from world import World

# Importa interface com FiraSim
# from client import VSS

import matplotlib.pyplot as plt
import numpy as np
import logging
import time
from vision.receiver import FiraClient

from strategy.automaticReplacer import AutomaticReplacer

class Loop:
    def __init__(
        self, 
        loop_freq=90, 
        draw_uvf=False, 
        team_yellow=False, 
        team_side=1,
        immediate_start=False, 
        referee=False, 
        static_entities=False,
        port=5001,
        n_robots=3,
        control=False,
        debug = False,
        mirror=False,
        last_command = None, #comando de STOP do REFEREE
        initiated_once = False
    ):
        # Instancia interface com o simulador FIRASim
        #self.vss = VSS(team_yellow=team_yellow)


        # Instancia o mundo e a estratégia
        self.world = World(n_robots=n_robots, side=team_side, debug=debug,team_yellow=team_yellow, immediate_start=immediate_start, referee=referee,mirror=mirror)
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Instancia interfaces com o referee
        self.rc = RefereeCommands()
        # self.rp = RefereePlacement(team_yellow=team_yellow)
        self.arp = AutomaticReplacer(self.world)

        # Variáveis
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0
        self.visionclient = FiraClient()
        self.radio = SerialRadio(control = control, debug = self.world.debug)
        self.execute = False
        self.t0 = time.time()
        
        self.last_command = last_command
        self.initiated_once = initiated_once

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        if self.draw_uvf:
            self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            self.UVF_screen.initialiazeScreen()
            self.UVF_screen.initialiazeObjects()
        
    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        self.lastupdatecount = self.world.updateCount
        
        # Para verificar o tempo de loop:
        # print("loop ALP:",(time.time()-self.t0)*1000)
        # self.t0 = time.time()
        
        # Executa estratégia
        self.strategy.update()

        # Executa o controle
        control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None]
        if self.execute:
            for robot in self.world.raw_team: robot.turnOn()   
            self.radio.send(control_output)
        else:
            self.radio.send([(0,0) for robot in self.world.team])
            for robot in self.world.raw_team: robot.turnOff()

        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):
        message = self.visionclient.receive_frame()
        
        self.execute = True if message else False
        
        if self.execute: self.world.update(message.detection)
        
        if( (self.world.debug) and (self.world.referee)):
            print("------------------------------")
            print("Executando com referee:")
        else:
            print("-----------------------------")
            print("Executando sem referee:")
        
        if(self.world.referee):
        
            command = self.rc.receive()
            
            if(self.world.debug and command is not None):
                print(self.last_command)
                print(command)
            elif(self.world.debug and command is None and not self.initiated_once):
                print("NENHUM PACOTE RECEBIDO AINDA")
            
            if command is not None:
                
                self.last_command = command
                # obedece o comando e sai do busy loop
                
            self.strategy.manageReferee(self.arp, self.last_command, self.initiated_once)
            
            if(self.world.debug and self.last_command != None):
                print("REFEREE RODANDO")
                
                
        

            
        
        
        

    def draw(self):
        for robot in [r for r in self.world.team if r.entity is not None]:
            clientProvider().drawRobot(robot.id, robot.x, robot.y, robot.thvec_raw.vec[0], robot.direction)

        # Plota inimigos no ALP-GUI
        # for robot in self.world.enemies:
        #     clientProvider().drawRobot(robot.id+3, robot.x, robot.y, robot.thvec_raw.vec[0], 1, (0.6, 0.6, 0.6))

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