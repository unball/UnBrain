from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy
from UVF_screen import UVFScreen
from world import World

# Importa interface com FiraSim
from client import VSS

import matplotlib.pyplot as plt
import numpy as np
import logging
import time
import sys
from vision.receiver import FiraClient


class Loop:
    def __init__(self,
                loop_freq=60,
                draw_uvf=False,
                team_yellow=False,
                team_side=1,
                immediate_start=False,
                static_entities=False,
                firasim=False,
                vssvision=False,
                control=False,
                debug =False,
                mirror=False
            ):
        # Instancia interface com o simulador
        self.firasim = VSS(team_yellow=team_yellow)

        # Instancia interfaces com o referee
        self.rc = RefereeCommands()
        self.rp = RefereePlacement(team_yellow=team_yellow)

        # Instancia o mundo e a estratégia

        self.world = World(3, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, firasim=firasim, vssvision=vssvision, control=control, debug=debug, mirror=mirror)
        self.strategy = MainStrategy(self.world, static_entities=static_entities)

        # Variáveis
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.lastupdatecount = 0

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        if self.draw_uvf:
            self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            self.UVF_screen.initialiazeScreen()
            self.UVF_screen.initialiazeObjects()

    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        self.lastupdatecount = self.world.updateCount

        # Executa estratégia
        self.strategy.update()

        control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None]

        # Executa o controle
        if self.world.firasim: 
            self.firasim.command.writeMulti(control_output)

        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):
        if(self.world.firasim):
            message = self.firasim.vision.read()
            #if message is not None: print("mensagem FIRASim", message)
            self.execute = True if message else False
            if self.execute: self.world.FIRASim_update(message)
        

    def draw(self):
        for robot in [r for r in self.world.team if r.entity is not None]:
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