import random
import robosim

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm
from matplotlib.colors import LinearSegmentedColormap

import numpy as np
import os
import sys

# logging + filas (p/ suporte a threading)
import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from concurrent_log_handler import ConcurrentRotatingFileHandler
import atexit

from multiprocessing import Process, Queue
from functools import partial

class SystemTester:
    def __init__(self, world):
        self.world = world

        self.field_dims=(170*4, 130*4)

        # INICIALIZAÇÃO DO LOGGER E QUEUE #

        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # config do sistema de logging com fila p/ simulador
        log_queue = queue.Queue(-1)  # fila ilimitada
        queue_handler = QueueHandler(log_queue)

        ## Teste do logger - vc só precisa habilitar isso se vc suspeitar que o logger está com algum problema de permissão no seu computador
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     handlers=[
        #         logging.FileHandler("app_test.log"),  # novo arquivo de teste
        #         logging.StreamHandler(sys.stdout)
        #     ],
        #     force=True  # Força redefinição de configurações anteriores
        # )
        # 
        # logging.debug("TESTE: Logging básico está funcionando?")

        # limpa o log passado
        with open('app.log', 'w') as f:
            pass  # só trunca o arquivo, pra limpar ele

        # cria handler do listener assíncrono para controlar gargalo de forma concorrente
        # o log é jogado pro arquivo app.log
        handler = ConcurrentRotatingFileHandler('app.log', maxBytes=1e6, backupCount=2, encoding='utf-8')

        global queue_listener
        queue_listener = QueueListener(log_queue, handler)

        # config formatação
        formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(message)s')
        queue_listener.handlers[0].setFormatter(formatter)

        # inicia listener em uma thread separada
        queue_listener.start()

        # config global
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(queue_handler)

        # print("Handlers ativos:", logging.getLogger().handlers)
        atexit.register(lambda: queue_listener.stop()) # desliga listener pra garantir que app.log fique disponível na próx execução

        ###################################

    def run_singletest(self, loop, robot_i, render_uvf=True, loop_freq=1/120):
        self.robot_i=robot_i # id do robô a ser monitorado
        self.simulado = loop.simulado
        plt.ion()
        plt.show(block=False)
        while loop.running:
            if self.simulado and self.world.ball.x > 0.75:
                print("GOL\n")
                self.simulado.reset([0.0, random.uniform(0.0, 0.3), 0.0, 0.0], [[-random.uniform(0.0, 0.3), random.uniform(0.0, 0.3), random.uniform(0.0, 0.3)], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]], [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
            # print(self.world.raw_team[0].field)
            robot = self.world.raw_team[self.robot_i]

            ax_static = plt.gca()
            ax_dynamic = plt.gca()
            if render_uvf:
                self.arrow_spaces=20
                x = np.arange(-self.field_dims[0]/2, self.field_dims[0]/2, self.arrow_spaces)
                y = np.arange(-self.field_dims[1]/2, self.field_dims[1]/2, self.arrow_spaces)
                X, Y = np.meshgrid(x, y)
                self.arrow_positions = np.array([X.flatten(), Y.flatten()]).T
                self.positions = []
                for i in range(self.arrow_positions.shape[0]):
                    self.positions.append(self.arrow_positions[i]/400)
                angles = list(map(robot.field.F, self.positions))
                pltuvf = plt.quiver(X, Y, np.cos(angles), np.sin(angles))
            else:
                ax_static.set_xlim([-360.0, 360])
                ax_static.set_ylim([-270.0, 270])

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
                    ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="blue", linewidth=3))
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
            plt.pause(loop_freq)

            if render_uvf:
                pltuvf.remove()
                del pltuvf

            ax_dynamic.remove()
            del ax_dynamic

    # [-0.725, 0.815], [-0.725, 0.615]] # valores do campo pré-"correção"
    def gera_randommatrix(self, a: float, b: float, size: int, timeout: float = 5.0) -> np.ndarray:
        '''
        Função que gera matriz de números aleatórios com {size} elementos.
        O timeout pode ser definido via parâmetro, que caso não definido será de 5 segundos e não produzirá aviso caso seja excedido.

        Usado em geração de nums aleatórios para randomizar instâncias de simulação.
        '''
        def _worker(q, a, b, size):
            try:
                buffer = os.urandom(size * 8)
                uint64_array = np.frombuffer(buffer, dtype=np.uint64)
                float_array = uint64_array.astype(np.float64) / (2**64)
                result = a + float_array * (b - a)
                q.put(result)
            except Exception as e:
                q.put(e)

        # serializa processo para evitar engasgar a thread
        q = Queue()
        worker_args = partial(_worker, q, a, b, size)
        p = Process(target=worker_args, daemon=True)
        
        p.start()
        p.join(timeout=timeout)
        
        if p.is_alive():
            p.terminate()
            p.join()
            flag = False
            if timeout < 5.0:
                raise TimeoutError(f"A geração da matriz de valores aleatórios excedeu o timeout de {timeout} segundos")
        else:
            flag = True
        
        result = q.get()
        
        if isinstance(result, Exception):
            raise result
        return result, flag
    
    def gera_heatmap(self, x_list, y_list):
        '''
            Função que gera o heatmap. Aviso:
            A função só *gera* o heatmap. Se você desejar que ele seja mostrado na tela, após chamar a função você deve usar o método show() do matplotlib.
        '''
        plt.figure(figsize=(12, 8), facecolor="white")
        ax_static = plt.gca()
        ax_static.set_facecolor("#006400")
        heatmap, xedges, yedges = np.histogram2d(x_list, y_list, bins=60, range=[[-0.850, 0.850], [-0.650, 0.650]])
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        cores = [
            (0.0, '#006400'),   # Verde puro
            (0.6, '#FFFF00'),   # Amarelo forte
            (0.8, '#FF8000'),   # Laranja
            (1.0, '#FF0000')    # Vermelho
        ]

        cmap_custom = LinearSegmentedColormap.from_list('green_yellow_red', cores)
        # Plotar o heatmap
        # aqui o heatmap está como heatmap+1 para contornar valores nulos (já que estamos usando uma escala de cores logaritmica)
        # limites do campo do simulado: [-0.725, 0.725, -0.615, 0.615]
        log_norm = LogNorm(vmin=1, vmax=np.max(heatmap)+1)
        im = ax_static.imshow(heatmap.T + 1 , extent=extent, origin='lower', cmap=cmap_custom, aspect='auto', norm=log_norm)
        cbar = plt.colorbar(im, ax=ax_static, cmap=cmap_custom)

        # escala simulador -> plot
        # não aconselho mexer nisso
        SCALE_FACTOR_X = 0.85 / 340  # 360 unidades do plot = 0.87m do simulado
        SCALE_FACTOR_Y = 0.65 / 256   # 270 unidades do plot = 0.65m do simulado

        # adiciona elementos do campo (linhas de gol, campo e etc)
        ax_static.set_xlim([-360.0*SCALE_FACTOR_X, 360*SCALE_FACTOR_Y])
        ax_static.set_ylim([-270.0*SCALE_FACTOR_X, 270*SCALE_FACTOR_Y])

        mid = Circle((0, 0), radius=3/400, color='black', alpha=1, zorder=10)
        ax_static.add_patch(mid)

        marcas = [(-380*SCALE_FACTOR_X, 430*SCALE_FACTOR_Y),
                (380*SCALE_FACTOR_X, 430*SCALE_FACTOR_Y),
                (-380*SCALE_FACTOR_X, -430*SCALE_FACTOR_Y),
                (380*SCALE_FACTOR_X, -430*SCALE_FACTOR_Y)] # marcas que tem no campo (aquelas bolinhas e "+" que tem no campo)
        
        limites = [[(-300*SCALE_FACTOR_X, -256*SCALE_FACTOR_Y), (-300*SCALE_FACTOR_X, 256*SCALE_FACTOR_Y)], 
                    [(-300*SCALE_FACTOR_X, 256*SCALE_FACTOR_Y), (300*SCALE_FACTOR_X, 256*SCALE_FACTOR_Y)], 
                    [(300*SCALE_FACTOR_X, -256*SCALE_FACTOR_Y), (300*SCALE_FACTOR_X, 256*SCALE_FACTOR_Y)], 
                    [(-300*SCALE_FACTOR_X, -256*SCALE_FACTOR_Y), (300*SCALE_FACTOR_X, -256*SCALE_FACTOR_Y)]] # Linhas do campo
        
        gol_amarelo = [[(340*SCALE_FACTOR_X, -80*SCALE_FACTOR_Y), (340*SCALE_FACTOR_X, 80*SCALE_FACTOR_Y)], 
                        [(300*SCALE_FACTOR_X, -80*SCALE_FACTOR_Y), (300*SCALE_FACTOR_X, 80*SCALE_FACTOR_Y)]] # Linhas do gol amarelo
        
        gol_azul = [[(-340*SCALE_FACTOR_X, -80*SCALE_FACTOR_Y), (-340*SCALE_FACTOR_X, 80*SCALE_FACTOR_Y)], 
                    [(-300*SCALE_FACTOR_X, -80*SCALE_FACTOR_Y), (-300*SCALE_FACTOR_X, 80*SCALE_FACTOR_Y)]] # Linhas do gol azul
        
        for pos in marcas:
            plt.gca().add_patch(Circle(xy=pos,radius=4/400, color="black", alpha=1, zorder=10))
        for pos in limites:
            ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="white", linewidth=2, zorder=10))
        for pos in gol_amarelo:
            if self.world.team_yellow:
                ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="blue", linewidth=3, zorder=10))
            else:
                ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="yellow", linewidth=3, zorder=10))
        for pos in gol_azul:
            if self.world.team_yellow:
                ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="yellow", linewidth=3, zorder=10))
            else: 
                ax_static.add_line(Line2D(*zip(pos[0],pos[1]), color="blue", linewidth=3, zorder=10))
        center_line = Line2D(*zip((0, -256*SCALE_FACTOR_Y), (0, 256*SCALE_FACTOR_Y)), color="gray", linewidth=1)
        center_circle = Circle((0, 0), 80/400, facecolor='None', edgecolor='white', linewidth=1, zorder=10)
        ax_static.add_line(center_line)
        ax_static.add_patch(center_circle)

        # config do gráfico
        plt.title('Heatmap')
        plt.xlabel('Largura do campo')
        plt.ylabel('Comprimento do campo')
        plt.grid(True, color="#228B22", alpha=1.0)

    def gera_datadict(self, register_dict : dict) -> dict: 
        '''
        estatística dos dados coletados durante o jogo
        '''
        runningtime_register = register_dict["runningtime"]
        goal_aliado = register_dict["goalcount aliado"]
        goal_inimigo = register_dict["goalcount inimigo"]
        stuckball_register = register_dict["stuckball"]

        # calcula tempo total rodando simulação (contando erros que param a thread)
        total_runningtime = sum(runningtime_register)
        formatted_runningtime = f"{int(total_runningtime//3600):02d}" + "h" + f"{int((total_runningtime%3600)//60):02d}" + "m" + f"{int(total_runningtime%60):02d}" + "s" # formata de float em segundos p/ string no formato XXhXXmXXs

        # salva lista com intervalos entre reset e gols, e posteriormente quantidade de gols também
        goal_intervals_aliado = [interval 
                          for thread_intervals in goal_aliado
                            for interval in thread_intervals]
        goal_intervals_mean_aliado = sum(goal_intervals_aliado)/len(goal_intervals_aliado) if len(goal_intervals_aliado) != 0 else 0
        quant_goals_aliado = len(goal_intervals_aliado)
        goal_intervals_inimigo = [interval 
                          for thread_intervals in goal_inimigo
                            for interval in thread_intervals]
        goal_intervals_mean_inimigo = sum(goal_intervals_inimigo)/len(goal_intervals_inimigo) if len(goal_intervals_inimigo) != 0 else 0
        quant_goals_inimigo = len(goal_intervals_inimigo)

        # salva lista com duração de movimento das bolas em cada thread
        moving_ball_times = [interval 
                          for thread_intervals in stuckball_register
                            for interval in thread_intervals]
        moving_ball_mean = sum(moving_ball_times)/len(moving_ball_times) if len(moving_ball_times) != 0 else 0

        # dicionário a ser retornado com os dados necessários para cálculo das estatísticas de simulação
        data_dict = {"runningtime": formatted_runningtime,
                                 "goalcount_aliado": quant_goals_aliado,
                                 "goalinterval_mean_aliado": goal_intervals_mean_aliado,
                                 "goalcount_inimigo": quant_goals_inimigo,
                                 "goalinterval_mean_inimigo": goal_intervals_mean_inimigo,
                                 "movingball_mean": moving_ball_mean}
        return data_dict
    
    # método Random Matrix legado (sem timeout error)
    # def gera_randommatrix(self, a: float, b: float, size: int) -> np.ndarray:
    #     # gera bytes aleatórios, 8 bytes por número
    #     buffer = os.urandom(size * 8)
    #     # bytes para um array de inteiros de 64 bits
    #     uint64_array = np.frombuffer(buffer, dtype=np.uint64)
    #     # converte pra floats no intervalo (0.0, 1.0)
    #     float_array = uint64_array.astype(np.float64) / (2**64)
        
    #     # escala o array para o intervalo ab
    #     return a + float_array * (b - a)




# UVFScreen legado abaixo


# import os
# os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# from .pygame_tools import *
# import math
# import numpy as np
# import pygame

# class UVFScreen:
#     def __init__(self, world, index_uvf_robot = 2, arrow_step = 0.04):
#         self.world = world
#         self.index_uvf_robot = index_uvf_robot
#         self.arrow_step = int(arrow_step*M_TO_PIXEL)
#         self.arrow_poses = self.arrowPoses(arrow_step*M_TO_PIXEL)

#     def arrowPoses(self, arrow_step):
#         x = np.arange(-FIELD_DIMENSIONS[0]/2, FIELD_DIMENSIONS[0]/2, arrow_step)
#         y = np.arange(-FIELD_DIMENSIONS[1]/2, FIELD_DIMENSIONS[1]/2, arrow_step)
#         X,Y = np.meshgrid(x, y)
#         XY = np.array([X.flatten(), Y.flatten()]).T

#         return XY

#     def initialiazeScreen(self):
#         pygame.init()

#         self.screen =  pygame.display.set_mode(FIELD_DIMENSIONS)
    
#     def initialiazeObjects(self):
#         #cria shapes para poder perceber que a rotação está acontecendo
#         self.robotCollor = {0: (100,0,0),
#                             1: (0,100,0),
#                             2: (0,0,100)}
        
#         self.createRobotsSurface()
#         self.createUVFSurface()

#     def clearScreen(self):
#         #clear screen at the start of every frame
#         self.screen.fill((40, 40, 40))

#     def createRobotsSurface(self):
#         self.robots_surf = []
        
#         for index, robot in enumerate(self.world.raw_team):
#             if index == MAX_ROBOTS_NUMBER:
#                 break

#             #create new surface with white BG
#             self.robots_surf.append(pygame.Surface(ROBOT_DIMENSIONS))
#             self.robots_surf[index].fill((255,255,255))

#             #set a color key for blitting
#             self.robots_surf[index].set_colorkey((255, 0, 255))

#             #create shapes so you can tell rotation is happenning
#             robotMask1 =  pygame.Rect(ROBOT_DIMENSIONS[1]*2/3, ROBOT_DIMENSIONS[1]/3, 2.5*CM_TO_PIXEL, 2.5*CM_TO_PIXEL)
#             robotMask2 =  pygame.Rect(0, ROBOT_DIMENSIONS[1]*0.4375, int(7.5*CM_TO_PIXEL), int(0.75*CM_TO_PIXEL))

#             #draw the shape to that surface
#             pygame.draw.rect(self.robots_surf[index], self.robotCollor[index], robotMask1)
#             pygame.draw.rect(self.robots_surf[index], self.robotCollor[index], robotMask2)

#             #draw surf to screen and catch the rect that blit returns
#             blittedRect = self.screen.blit(self.robots_surf[index], centralField2pygameAxisCoordinate((robot.x,robot.y)))
    
#     def drawRobots(self):
#         for index, robot in enumerate(self.world.raw_team):
#             if index == MAX_ROBOTS_NUMBER:
#                 break

#             #rotate surf by DEGREE amount degrees
#             rotatedSurf =  pygame.transform.rotate(self.robots_surf[index], math.degrees(robot.th))

#             #get the rect of the rotated surf and set it's center to the oldCenter
#             rotRect = rotatedSurf.get_rect()
#             rotRect.center = centralField2pygameAxisCoordinate((robot.x*M_TO_PIXEL,robot.y*M_TO_PIXEL))

#             #draw rotatedSurf with the corrected rect so it gets put in the proper spot
#             self.screen.blit(rotatedSurf, rotRect)


#     def drawBall(self):
#         pygame.draw.circle(self.screen, (100, 0, 0), centralField2pygameAxisCoordinate((self.world.ball.x*M_TO_PIXEL, self.world.ball.y*M_TO_PIXEL)), BALL_RADIUS)

#     def createUVFSurface(self):
#         # self.arrows_surf = pygame.Surface((self.arrow_step, self.arrow_step))
#         # self.arrows_surf.fill((40,40,40))
#         # self.arrows_surf.set_colorkey((255, 255, 255))

#         # #create shapes so you can tell rotation is happenning
#         # robotMask =  pygame.Rect(ROBOT_DIMENSIONS[1]*2/3, ROBOT_DIMENSIONS[1]/3, 2.5*CM_TO_PIXEL, 2.5*CM_TO_PIXEL)

#         # #draw the shape to that surface
#         # # pygame.draw.rect(self.arrows_surf[index], (255,255,255), robotMask)
#         # pygame.draw.line(self.arrows_surf, (255,255,255), (0, self.arrow_step/2), (self.arrow_step-4, self.arrow_step/2))
#         # pygame.draw.circle(self.arrows_surf, (255,255,255), (int(self.arrow_step-4), int(self.arrow_step/2)), int(0.5*CM_TO_PIXEL))

#         # # #draw surf to screen and catch the rect that blit returns
#         # blittedRect = self.screen.blit(self.arrows_surf, centralField2pygameAxisCoordinate((0,0)))

#         self.arrows_surf = []
        
#         robot = self.world.raw_team[self.index_uvf_robot]

#         for index in range(self.arrow_poses.shape[0]):
#             #create new surface with white BG
#             self.arrows_surf.append(pygame.Surface((self.arrow_step, self.arrow_step)))
#             self.arrows_surf[index].fill((40,40,40))

#             # #set a color key for blitting
#             # self.arrows_surf[index].set_colorkey((255, 255, 255))

#             #draw the shape to that surface
#             # pygame.draw.rect(self.arrows_surf[index], (255,255,255), robotMask)
#             pygame.draw.line(self.arrows_surf[index], (255,255,255), (0, self.arrow_step/2), (self.arrow_step-4, self.arrow_step/2))
#             pygame.draw.circle(self.arrows_surf[index], (255,255,255), (int(self.arrow_step-4), int(self.arrow_step/2)), int(0.5*CM_TO_PIXEL))

#             # #draw surf to screen and catch the rect that blit returns
#             blittedRect = self.screen.blit(self.arrows_surf[index], centralField2pygameAxisCoordinate(self.arrow_poses[index]))


#     def drawUVF(self):
#         robot = self.world.raw_team[self.index_uvf_robot]

#         if robot.field is None: 
#             return

#         for index in range(self.arrow_poses.shape[0]):
#             #rotate surf by DEGREE amount degrees
#             th = robot.field.F(self.arrow_poses[index]/M_TO_PIXEL)
#             rotatedSurf =  pygame.transform.rotate(self.arrows_surf[index], math.degrees(th))

#             #get the rect of the rotated surf and set it's center to the oldCenter
#             rotRect = rotatedSurf.get_rect()
#             rotRect.center = centralField2pygameAxisCoordinate(self.arrow_poses[index])

#             #draw rotatedSurf with the corrected rect so it gets put in the proper spot
#             self.screen.blit(rotatedSurf, rotRect)

        
#     def updateScreen(self):        
#         self.clearScreen()

#         self.drawUVF()
#         self.drawRobots()
#         self.drawBall()

#         #show the screen surface
#         pygame.display.flip()