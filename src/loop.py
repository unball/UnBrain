from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy
from UVF_screen import UVFScreen
from world import World
from client import VSS

import matplotlib.pyplot as plt
import numpy as np
import logging
import time
import sys

class Loop:
    def __init__(self, loop_freq=60, draw_uvf=False, team_yellow=True, team_side=1, immediate_start=False, static_entities=False):
        # Instancia interface com o simulador
        self.vss = VSS(team_yellow=team_yellow)

        # Instancia interfaces com o referee
        self.rc = RefereeCommands()
        self.rp = RefereePlacement(team_yellow=team_yellow)

        # Instancia o mundo e a estratégia
        self.world = World(3, side=team_side, vss=self.vss, team_yellow=team_yellow, immediate_start=immediate_start)
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

        # Executa o controle
        if not self.draw_uvf: 
            self.vss.command.writeMulti([robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None])
        else:
            self.vss.command.writeMulti([(0,0) for robot in self.world.team])

        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):
        message = self.vss.vision.read()
        if message is not None: self.world.update(message)
        
        command = self.rc.receive()
        if command is not None: self.strategy.manageReferee(self.rp, command)

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