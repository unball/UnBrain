from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy, Attacker, Defender, GoalKeeper, AI_Attacker
from UVF_screen import SystemTester
from communication.serialWifi import SerialRadio
from world import World
import math

import threading

# Importa interface com FiraSim
from client import VSS

import random
import robosim
import torch

# matplotlib

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

import random

from state_predictor_project.state_predictor import CommandLogger, FrameLogger, StatePredictor
import time

from strategy.automaticReplacer import AutomaticReplacer

import constants

class Loop:

    def __init__(self,
                loop_freq=200, #Para uso de IA, tem que aumentar o FPS para rodar +próximo de 60 FPS
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
                AI_attacker=False,
                enemy_AI= False,
                test_type=False,
                use_predictor=False
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

        self.use_predictor = use_predictor

        self.cmd_logger = CommandLogger()
        self.frame_logger = FrameLogger()
        self.predictor = StatePredictor(
            cmd_logger=self.cmd_logger,
            frame_logger=self.frame_logger,
            tau_act=0.02,        
            use_residual=False,   # [CORREÇÃO] AGORA A REDE NEURAL ESTÁ LIGADA!
            model_path="src/state_predictor_project/state_predictor/firasim_residual_model.pth" 
        )
        
        # ===== TESTES / A-B / DEBUG =====
        self.use_pred_in_ai = False       # Começa desligado (Baseline)
        self.current_mode = "A_RAW"
        
        self.inject_firasim_delay = 0.02  # 50ms de delay para forçar o erro e ver a rede atuar
        self._last_frame_t = None         

        self.vision_queue = []
        self._dbg_last_print_t = time.monotonic()
        self._dbg_acc = {"n": 0, "sum_dt": 0.0, "sum_err": 0.0, "max_dt": 0.0, "max_err": 0.0}

        # [ENG] Estrutura dupla para validação comparativa
        self.metrics = {
            "A_RAW":  {"distancias": [], "tempos_gol": [], "stuck_ball": [], "gols_aliados": 0, "gols_inimigos": 0},
            "B_PRED": {"distancias": [], "tempos_gol": [], "stuck_ball": [], "gols_aliados": 0, "gols_inimigos": 0}
        }

        self.last_ball_x = []
        self.last_ball_y = []

        # Instancia interface com o simulador
        if firasim: self.firasim = VSS(team_yellow=team_yellow)
        if simulado:
            yellow_robots_pos = []
            blue_robots_pos = []
            field_type = 0  # 0 for Division B, 1 for Division A
            pos = [[-0.6, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.2, 0.0, 0.0]]
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
    
        if vssvision: self.visionclient = FiraClient()
        # Instancia o mundo e a estratégia

        team_side = -1 if mirror else 1
        self.team_side = team_side
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, referee=referee, firasim=firasim, vssvision=vssvision, mainvision=mainvision, simulado=simulado, control=control, debug=debug, mirror=mirror,AI_attacker=AI_attacker, enemy_AI=enemy_AI)

        # [ENG] Inicializando os cronômetros do episódio
        self.tempo_inicio_episodio = time.time()
        self.fps_cmd_count = 0
        self.fps_last_time = time.time()

        if referee:
                self.rc = RefereeCommands()
                self.rp = RefereePlacement(team_yellow=team_yellow)

        self.strategy = MainStrategy(self.world, static_entities=static_entities, AI_attacker=AI_attacker)

        # Variáveis
        self.message = None
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.execute = False
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

    def x(self, begin=-0.75 + 0.1, end=0.75 - 0.1):
        return random.uniform(begin, end)

    def y(self, begin=-0.65 + 0.1, end=0.65 - 0.1):
        return random.uniform(begin, end)

    def theta(self):
        return random.uniform(0, 360)

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

        print("\n" + "="*60)
        print(" RELATÓRIO FINAL DO EXPERIMENTO A/B (Rede Neural)")
        print("="*60)
        print(f"Delay Injetado: {self.inject_firasim_delay * 1000} ms")
        print("-" * 60)
        
        for mode in ["A_RAW", "B_PRED"]:
            m = self.metrics[mode]
            dist_media = np.mean(m["distancias"]) if m["distancias"] else 0
            t_gol = np.mean(m["tempos_gol"]) if m["tempos_gol"] else 0
            total_tentativas = m["gols_aliados"] + m["gols_inimigos"] + len(m["stuck_ball"]) + 1e-5
            taxa = m["gols_aliados"] / total_tentativas
            
            print(f"MODO: {mode}")
            print(f"  Gols (Aliados/Inimigos): {m['gols_aliados']} / {m['gols_inimigos']}")
            print(f"  Stuck Balls:             {len(m['stuck_ball'])}")
            print(f"  Tempo Médio p/ Gol:      {t_gol:.2f} s")
            print(f"  Distância Média à Bola:  {dist_media:.4f} m")
            print(f"  Taxa de Sucesso:         {taxa*100:.1f} %")
            print("-" * 60)
        print("="*60 + "\n")

        # ... (restante dos turnOff e sys.exit) ...
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

    # =========================================================================
    # [UNBALL - CONTROL ENG] Gerenciamento Dinâmico do Preditor de Estado
    # =========================================================================
    def set_predictor_state(self, state: bool):
        """
        Liga ou desliga o preditor de estado em tempo de execução.
        Limpa os buffers (Bumpless Transfer) para evitar pulos indesejados.
        """
        if state and not getattr(self, 'use_predictor', False):
            # Limpa o passado (histórico) recriando as instâncias
            self.cmd_logger = CommandLogger()
            self.frame_logger = FrameLogger()
            self.predictor = StatePredictor(
                cmd_logger=self.cmd_logger,
                frame_logger=self.frame_logger,
                tau_act=0.05,
                use_residual=False
            )
            self.last_frame_time = time.monotonic()
            print("\n[ENG] >>> PREDITOR DE ESTADO LIGADO <<<")
            
        elif not state and getattr(self, 'use_predictor', True):
            print("\n[ENG] >>> PREDITOR DE ESTADO DESLIGADO (Usando Visão Crua) <<<")
            
        self.use_predictor = state

    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        self.t0 = time.time()
        self.lastupdatecount = self.world.updateCount

        # Executa estratégia
        self.strategy.update(self.world)

        atacante = self.world.team[self.n_robots[0]] 
        bola = self.world.ball

        if atacante is not None and bola is not None:
            # Calcula a distância euclidiana entre a IA e a Bola
            dx = bola.x - atacante.x
            dy = bola.y - atacante.y
            dist = (dx**2 + dy**2) ** 0.5
            # Salva na métrica do modo atual (A_RAW ou B_PRED)
            self.metrics[self.current_mode]["distancias"].append(dist)

        # Gera os comandos de atuação (control_output) 
        if self.world.mainvision: control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot is not None]
        if self.world.firasim: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]
        if self.world.simulado: control_output = [robot.entity.control.actuateSimu(robot) for robot in self.world.team if robot is not None]

        # =====================================================================
        # EXECUÇÃO DO CONTROLE & [ENG] LOG DE FEEDBACK DE COMANDO
        # =====================================================================
        if self.world.firasim:
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.firasim.command.writeMulti(control_output)
                
                # [ENG] Registrar Feedback FIRASim para integral do Preditor
                t_send = time.monotonic()
                for i, robot_id in enumerate(self.world.n_robots):
                    if i < len(control_output): 
                        v_cmd, w_cmd = control_output[i]
                        self.cmd_logger.push(robot_id, v_cmd, w_cmd, t_send)

        if self.world.mainvision:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.radio.send(self.world.n_robots, control_output)
                
                # [ENG] Registrar Feedback MainVision para integral do Preditor
                t_send = time.monotonic()
                for i, robot_id in enumerate(self.world.n_robots):
                    if i < len(control_output):
                        v_cmd, w_cmd = control_output[i]
                        self.cmd_logger.push(robot_id, v_cmd, w_cmd, t_send)
                        
        if self.world.simulado:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
            self.control_output = control_output
            self.simulado.step(control_output)
        
        if self.world.debug and constants.DEBUG_ACTUATE:
            contador = 0
            for v1, v2 in control_output:
                print(f"ACTUATE DO ROBO {contador} | V {v1:.2f} | W {v2:.2f}")
                contador+=1

        # Desenha no ALP-GUI
        self.draw()

    def busyLoop(self):

        if self.world.firasim:
            # 1. Lê os pacotes da rede O MAIS RÁPIDO POSSÍVEL (sem sleep!)
            message = self.firasim.vision.read()
            
            if message:
                t_frame_real = time.monotonic() 
                # Guarda o frame e a hora que ele chegou na fila
                self.vision_queue.append((t_frame_real, message))

            self.execute = False

            # 2. Só processa a mensagem se ela tiver a "idade" do nosso delay
            if len(self.vision_queue) > 0:
                t_oldest, oldest_msg = self.vision_queue[0]
                
                # Verifica se o frame mais antigo já esperou os 50ms (ou o valor injetado)
                if (time.monotonic() - t_oldest) >= self.inject_firasim_delay:
                    
                    # Retira o frame da fila para o jogo finalmente processar
                    self.vision_queue.pop(0)
                    
                    self.message = oldest_msg
                    self.execute = True
                    self.last_frame_time = t_oldest
                    
                    # =================================================================
                    # [UNBALL] INTERCEPTAÇÃO DE PACOTE E PREDITOR DE ESTADO
                    # =================================================================
                    if getattr(self, 'use_predictor', False):
                        t_now = time.monotonic()
                        dt_frame = t_now - t_oldest

                        # 1. BOLA: Extrapolação baseada nas velocidades nativas
                        if hasattr(self.message, 'frame') and hasattr(self.message.frame, 'ball'):
                            self.message.frame.ball.x += float(self.message.frame.ball.vx * dt_frame)
                            self.message.frame.ball.y += float(self.message.frame.ball.vy * dt_frame)

                        # 2. ROBÔS: Log da verdade e injeção da Predição
                        robots_team = self.message.frame.robots_yellow if self.team_yellow else self.message.frame.robots_blue

                        for r in robots_team:
                            self.frame_logger.push(r.robot_id, r.x, r.y, math.radians(r.orientation), t_oldest)

                            # [ENG] Desliga o preditor se o robô estiver 'colado' na bola (Manobra Fina)
                            dist_para_bola = ((r.x - self.message.frame.ball.x)**2 + (r.y - self.message.frame.ball.y)**2)**0.5
                            
                            # Se estiver a mais de 7cm da bola, usa o preditor para cortar o lag.
                            # Se estiver muito perto, usa a visão crua para evitar o "chattering".
                            if dist_para_bola > 0.07:
                                pose_est = self.predictor.estimate_now(r.robot_id, t_now)

                                if pose_est is not None:
                                    est_x, est_y, est_th = pose_est
                                    r.x = float(est_x)
                                    r.y = float(est_y)
                                    r.orientation = float(math.degrees(est_th))
                    # =================================================================
                    
                    # O UnBrain agora chamará internamente os métodos .updateSimu() com dados corretos!
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
            try:
                message = self.pclient.receive()
                self.message = message if message is not None else self.message
                self.execute = self.message["running"] if self.message is not None else False
                # print(self.message)
            except ConnectionError:
                self.handle_SIGINT(0,0, shutdown=True)     
            if self.execute == False: # Se a visão parar de rodar, o robô para ao invés de continuar com o último comando
                self.handle_SIGINT(0,0, shutdown=False)
            elif self.message is not None: 
                # [ENG] Timestamp da recepção do frame da MainVision
                t_cap = time.monotonic()
                self.last_frame_time = t_cap
                
                self.world.update_main_vision(self.message)
                
                # Injeta a pose da visão no buffer
                for robot in self.world.raw_team:
                    if robot is not None:
                        self.frame_logger.push(robot.id, robot.x, robot.y, robot.th, t_cap)

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
                self.strategy.manageReferee(self.world.last_command)

    def reset_firasim_episode(self):
        """Teletransporta a bola e robôs no FIRASim para iniciar novo episódio limpo"""
        if self.world.firasim and hasattr(self, 'firasim'):
            # 1. Posições aleatórias para a bola (Centro do campo, variando levemente)
            bx = random.uniform(-0.1, 0.1)
            by = random.uniform(-0.3, 0.3)
            self.firasim.command.setBallPos(bx, by)
            
            # 2. Reposiciona os Robôs para o campo de defesa!
            # Vamos adicionar um pequeno 'ruído' no Y para que a IA 
            # não vicie em sair sempre de uma linha reta perfeita.
            if len(self.n_robots) > 0:
                # Atacante (n_robots[0]) começa no meio do campo de defesa
                ry_0 = random.uniform(-0.1, 0.1)
                self.firasim.command.setPos(self.n_robots[0], -0.3, ry_0, 0.0)
                
            if len(self.n_robots) > 1:
                # Zagueiro/Goleiro 1
                self.firasim.command.setPos(self.n_robots[1], -0.6, 0.15, 0.0)
                
            if len(self.n_robots) > 2:
                # Zagueiro/Goleiro 2
                self.firasim.command.setPos(self.n_robots[2], -0.6, -0.15, 0.0)
            
        # 3. Reseta cronômetros e histórico de stuck ball para não carregar lixo da jogada anterior
        self.tempo_inicio_episodio = time.time()
        self.last_ball_x.clear()
        self.last_ball_y.clear()

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

        firasim_ab_test = (self.test_type == "firasim_ab")
        intervalo_ab = 60 # 60 segundos avaliando cada modo

        while self.running:
            now_time = time.time()
            tempo_decorrido_global = now_time - tempo_zero
            tempo_decorrido = now_time - self.tempo_inicio_episodio

            # =================================================================
            # CHAVEAMENTO A/B AUTOMÁTICO
            # =================================================================
            if firasim_ab_test:
                novo_estado = (int(tempo_decorrido_global / intervalo_ab) % 2) == 1
                if novo_estado != self.use_pred_in_ai:
                    self.use_pred_in_ai = novo_estado
                    self.current_mode = "B_PRED" if self.use_pred_in_ai else "A_RAW"
                    print(f"\n[🔄 CHAVEAMENTO] Mudando para o modo: {self.current_mode}")
                    # Ao trocar o modo, limpamos os buffers da rede para evitar pulos
                    self.cmd_logger = CommandLogger()
                    self.frame_logger = FrameLogger()
                    self.reset_firasim_episode() 
            # =================================================================

            if tempo_decorrido > 1.0: 
                # 1. Verifica STUCK BALL
                if tempo_decorrido > 5.0:
                    self.last_ball_x.append(self.world.ball.x)
                    self.last_ball_y.append(self.world.ball.y)
                    if len(self.last_ball_x) > 30:
                        self.last_ball_x.pop(0)
                        self.last_ball_y.pop(0)
                        
                        if np.std(self.last_ball_x) < 1e-3 and np.std(self.last_ball_y) < 1e-3:
                            print(f">>> [{self.current_mode}] STUCK BALL DETECTADO! (Tempo: {tempo_decorrido:.2f}s) Reiniciando...")
                            self.metrics[self.current_mode]["stuck_ball"].append(tempo_decorrido)
                            self.reset_firasim_episode()

                # 2. Verifica GOL ALIADO 
                if hasattr(self.world, 'ball') and self.world.ball.x > 0.75:
                    print(f">>> [{self.current_mode}] GOL ALIADO! Tempo: {tempo_decorrido:.2f}s")
                    self.metrics[self.current_mode]["gols_aliados"] += 1
                    self.metrics[self.current_mode]["tempos_gol"].append(tempo_decorrido)
                    self.reset_firasim_episode()

                # 3. Verifica GOL INIMIGO 
                elif hasattr(self.world, 'ball') and self.world.ball.x < -0.75:
                    print(f">>> [{self.current_mode}] GOL INIMIGO! Tempo: {tempo_decorrido:.2f}s")
                    self.metrics[self.current_mode]["gols_inimigos"] += 1
                    self.reset_firasim_episode()

            if self.world.simulado == True and not self.test_type:
                if time.time() - self.tempo_repos > 30 and not self.contagem == 100:
                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]
                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.tempo_repos = time.time()
                    self.contagem += 1
                    print(f'\n{self.contagem}')
                    self.simulado.reset(pos_ball, pos_robots, [[]])
                elif self.world.ball.x > self.world.field.goalPos[0] and not self.contagem == 100:
                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]
                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.simulado.reset(pos_ball, pos_robots, [[]])
                    self.tempo_repos = time.time()
                    self.contagem += 1
                    self.gol_a_favor += 1
                    print(f'\n{self.contagem}')
                elif self.world.ball.x < -self.world.field.goalPos[0] and not self.contagem == 100:
                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]
                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.simulado.reset(pos_ball, pos_robots, [[]])
                    self.tempo_repos = time.time()
                    self.contagem += 1
                    self.gol_contra += 1
                    print(f'\n{self.contagem}')
                if self.contagem == 100:
                    print(f'\nEm {self.contagem} testes, {self.gol_a_favor} gols feitos e {self.gol_contra} gols contra.')
            
            # Executa o loop de visão e referee até dar o tempo de executar o resto
            self.busyLoop()
            while time.time() - t0 < self.loopTime:
                self.loop()
                self.busyLoop()
                # self.data_colector.collect()
                
            self.world.execTime = time.time() - t0
                
            # Tempo inicial do loop
            t0 = time.time()

            # Executa o loop
            self.loop()

            print(f"gfl {time.time()-tempo_zero:.2f} FPS:{1/self.world.execTime:.2f}", end="\r", flush=True)
            # if time.time()-tempo_zero > 1:
            #     self.running = False

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
            field_type = 0 

            time_step_ms = 16

            last_ball_xs = []
            last_ball_ys = []
            pos_robots = []
            pos_ball = [self.x(), self.y(), 0.0, 0.0]

            for i in self.world.n_robots:
                pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola

            # inicializa ambiente do simulado
            self.simulado = robosim.VSS(
                field_type,
                len(self.n_robots),
                0,
                time_step_ms,
                pos_ball,
                pos_robots,
                [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]],
            )

            ball_x, ball_y = self.simulado.get_state()[0], self.simulado.get_state()[1]
            
            logger.info("System is running")

            cronometro_5s, cronometro_1s = self.tempo_atual, self.tempo_atual
            last_reset_time = -1
            while self.tempo_atual < duracao:
                self.tempo_atual = time.time()-tempo_zero
                flag_1s, flag_5s = False, False
                # numeros, flag = tester.gera_randommatrix(a= -0.3, b= 0.3, size=13)
                
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

                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]

                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.simulado.reset(pos_ball,
                                        pos_robots, 
                                         [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    last_reset_time =  self.tempo_atual

                if hasattr(self, 'simulado') and self.world.ball.x > 0.75:
                                        
                    logger.info(f"GOL Aliado na thread {thread_id}")

                    goal_interval = self.tempo_atual - last_reset_time if last_reset_time != -1 else self.tempo_atual - last_reset_time + 1
                    self.goal_register_aliado[thread_id].append(goal_interval)
                    # print(f"n_robots: {self.world.n_robots}")

                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]

                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.simulado.reset(pos_ball,
                                        pos_robots, 
                                         [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    # self.simulado.reset([0.0, numeros[0], 0.0, 0.0], [[-numeros[1], numeros[2], numeros[3]], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]], [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    last_reset_time = self.tempo_atual
                if hasattr(self, 'simulado') and self.world.ball.x < -0.75:
                                        
                    logger.info(f"GOL Inimigo na thread {thread_id}")
                    print('gol AI')

                    goal_interval = self.tempo_atual - last_reset_time if last_reset_time != -1 else self.tempo_atual - last_reset_time + 1
                    self.goal_register_inimigo[thread_id].append(goal_interval)
                    # print(f"n_robots: {self.world.n_robots}")

                    pos_robots = []
                    pos_ball = [self.x(), self.y(), 0.0, 0.0]

                    for i in self.world.n_robots:
                        pos_robots.append([self.x(), self.y(), self.theta()]) #posiçao da bola
                    self.simulado.reset(pos_ball,
                                        pos_robots, 
                                         [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    # self.simulado.reset([0.0, numeros[0], 0.0, 0.0], [[-numeros[1], numeros[2], numeros[3]], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]], [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]])
                    last_reset_time = self.tempo_atual


                self.busyLoop()
                while time.time() - t0 < self.loopTime:
                    self.loop()
                self.world.execTime = time.time() - t0
                    
                t0 = time.time()
                self.loop()
                print(f"gfl {time.time()-tempo_zero:.2f} FPS:{1/self.world.execTime}", end="\r", flush=True)


                # atualiza listas de posições
                self.team_positions = [(round(robot.x, 3), round(robot.y, 3)) 
                                    for robot in self.world.raw_team if robot is not None]
                
                for robot in self.world.raw_team:
                    if robot is not None:
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

    def test(self, n_threads=1):
            # inicializa testador
            tester = SystemTester(self.world)
            self.thread_envs = [[] for _ in range(n_threads)] # separação em threads para uso futuro, favor não desfazer isso
            self.all_positions = copy.deepcopy(self.thread_envs)
            self.goal_register_aliado = copy.deepcopy(self.thread_envs)
            self.goal_register_inimigo = copy.deepcopy(self.thread_envs)
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
                    if self.test_type == "heatmap_attacker_ia":
                        loop_thread = threading.Thread(target=self.run_parallel, args=(tester, i, AI_Attacker), daemon=True)
                    elif self.test_type == "heatmap_attacker":
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
                                 "goalcount aliado": self.goal_register_aliado,
                                 "goalcount inimigo": self.goal_register_inimigo,
                                 "stuckball": self.stuckball_register}
                
                data_dict = tester.gera_datadict(register_dict)

                # print mais bonitinho dos dados
                for key, value in data_dict.items():
                    print(f"{key}: {value}")

                plt.show()
