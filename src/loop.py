from client.referee import RefereeCommands, RefereePlacement
from client.gui import clientProvider
from strategy import MainStrategy, Attacker, Defender, GoalKeeper, AI_Attacker
from UVF_screen import SystemTester
from communication.serialWifi import SerialRadio
from world import World
import math

import multiprocessing

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
import csv
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

from state_predictor_project.vision_interceptor import VisionInterceptor
import time
from collections import deque
from tools import motors2speeds_from_vl_vr  # <-- necessário para logar (v,w) a partir de (vl,vr)

import constants

from system_test.collector import CollectorMixin

class Loop(CollectorMixin):

    def __init__(self,
                loop_freq=200, # FPS padrão. Será reduzido para 60 automaticamente no simulado/rsim para bater com a física.
                draw_uvf=False,
                team_yellow=False,
                immediate_start=True,
                static_entities=False,
                referee=False,
                firasim=False,
                travesim=False,
                rsim=False,
                simulado=False,
                mainsystem=False,
                control=False,
                debug =False,
                port=5002,
                mirror=False, 
                n_robots=[0,1,2],
                AI_attacker=False,
                enemy_AI= False,
                test_type=False,
                use_predictor=False,
                disable_ai=False,
                inject_delay=0.0,
                record=False,
                teleport=None,
                use_kalman=False,
                use_neural_estimator=False,
                timestep_ms=16
            ):
        
        self.loop_thread = None
        self.ws_thread = None
        self.threadScreen = None
        self.test_type = test_type

        # Guarda os parâmetros de construção para permitir recriar Loops idênticas
        # dentro de subprocessos (coleta de dados em paralelo via multiprocessing).
        # Threads não escalam aqui por causa do GIL + robosim em C++; processos sim.
        self._init_kwargs = dict(
            loop_freq=loop_freq, draw_uvf=draw_uvf, team_yellow=team_yellow,
            immediate_start=immediate_start, static_entities=static_entities,
            referee=referee, firasim=firasim, travesim=travesim, rsim=rsim,
            simulado=simulado, mainsystem=mainsystem, control=control, debug=debug,
            port=port, mirror=mirror, n_robots=n_robots, AI_attacker=AI_attacker,
            enemy_AI=enemy_AI, test_type=test_type, use_predictor=use_predictor,
            disable_ai=disable_ai, inject_delay=inject_delay, record=record,
            teleport=teleport, use_kalman=use_kalman,
            use_neural_estimator=use_neural_estimator,
            timestep_ms=timestep_ms
        )

        self.team_yellow = team_yellow
        self.team_change_cooldown = 0
        self.n_robots = n_robots
        self.referee = referee
        self.immediate_start = immediate_start
        self.control = control
        self.debug = debug
        self.mirror = mirror

        self.use_predictor = use_predictor
        self.record = record

        from tools.vision_noise import VisionNoiseSimulator
        self.vision_noise_simulator = VisionNoiseSimulator()
        self.noise_frame_counter = 0

        import socket
        import json
        self.noise_config_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # IMPORTANTE: setblocking(False) ANTES (e fora) do bind. Se o bind falha
        # (ex.: porta já usada por outra instância em multiprocessing), o socket
        # PRECISA continuar non-blocking, senão o recvfrom() do busyLoop() trava
        # para sempre esperando um pacote que nunca chega.
        self.noise_config_sock.setblocking(False)
        try:
            self.noise_config_sock.bind(('127.0.0.1', 20022))
        except Exception as e:
            print("\n Warning: noise config socket bind failed:", e)



        # ===== PREDITOR / TESTES A-B =====
        mode_str = "firasim" if firasim else ("travesim" if travesim else ("mainsystem" if mainsystem else "simulado"))
        self.vision_interceptor = VisionInterceptor(
            inject_delay=inject_delay if (firasim or travesim or simulado) else 0.0,
            lookahead=0.01,
            mode=mode_str,
            disable_ai=disable_ai,
            record=self.record
        )
        self.vision_interceptor.set_active(self.use_predictor)

        self.current_mode = "B_PRED" if self.use_predictor else "A_RAW"
        
        self._dbg_last_print_t = time.monotonic()
        self._dbg_acc = {"n": 0, "sum_dt": 0.0, "sum_err": 0.0, "max_dt": 0.0, "max_err": 0.0}

        # [ENG] Estrutura dupla para validação comparativa
        self.metrics = {
            "A_RAW":  {"distancias": [], "tempos_gol": [], "stuck_ball": [], "gols_aliados": 0, "gols_inimigos": 0},
            "B_PRED": {"distancias": [], "tempos_gol": [], "stuck_ball": [], "gols_aliados": 0, "gols_inimigos": 0}
        }    
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
        if travesim: self.travesim = VSS(team_yellow=team_yellow, is_travesim=True)
        if rsim or simulado:
            yellow_robots_pos = []
            blue_robots_pos = []
            field_type = 0  # 0 for Division B, 1 for Division A
            pos = [[-0.2, 0.0, 0.0], [-0.4, 0.0, 0.0], [-0.6, 0.0, 0.0]]
            if team_yellow:
                n_robots_yellow = len(n_robots)
                for i in n_robots:
                    yellow_robots_pos += [pos[i]]
                # Sempre 3 inimigos (azuis) fora do campo para que o estado rsim
                # tenha tamanho fixo (41 entradas) e _apply_restart possa reposicioná-los.
                n_robots_blue = 3
                blue_robots_pos = [[0.0, 2.0 + i * 0.2, 0.0] for i in range(3)]
            else:
                n_robots_blue = len(n_robots)
                for i in n_robots:
                    blue_robots_pos += [pos[i]]
                # Sempre 3 inimigos (amarelos) fora do campo.
                n_robots_yellow = 3
                yellow_robots_pos = [[0.0, 2.0 + i * 0.2, 0.0] for i in range(3)]
            self.rsim_time_step_ms = timestep_ms # time step in milliseconds
            # ball initial position [x, y, v_x, v_y] in meters and meter/s
            ball_pos = [0.0, 0.3, 0.0, 0.0]

            # robots initial positions [[x, y, angle], [x, y, angle]...], where [[id_0], [id_1]...]
            # Units are meters and degrees
            
            self.rsim = robosim.VSS(
                field_type,
                n_robots_blue,
                n_robots_yellow,
                self.rsim_time_step_ms,
                ball_pos,
                blue_robots_pos,
                yellow_robots_pos,
            )

        # field_params = self.rsim.get_field_params()
        # print(f"estado do campo:{self.rsim.get_state()}")

        # Instancia de sinal caso haja interrupções no processo (ctrl + C)
        try: 
            signal.signal(signal.SIGINT, self.handle_SIGINT)
        except ValueError:
            print("tentou chamar signal fora da thread principal")
        # Instancia interfaces com o referee
    
        if getattr(self, 'vssvision', False): self.visionclient = FiraClient()
        # Instancia o mundo e a estratégia

        team_side = -1 if mirror else 1
        self.team_side = team_side
        self.world = World(n_robots=n_robots, side=team_side, team_yellow=team_yellow, immediate_start=immediate_start, referee=referee, firasim=firasim, travesim=travesim, rsim=rsim, simulado=simulado, mainsystem=mainsystem, control=control, debug=debug, mirror=mirror,AI_attacker=AI_attacker, enemy_AI=enemy_AI, teleport_mode=teleport, flag_use_kalman=use_kalman, flag_use_neural_estimator=use_neural_estimator)

        # No rsim a física avança um passo fixo (rsim_time_step_ms) por step, mas
        # o velocity é estimado por diferença de posição. Usar o dt SIMULADO (e não
        # o de relógio) deixa a velocidade da observação independente do fps do loop.
        if hasattr(self, 'rsim_time_step_ms'):
            self.world.rsim_dt_s = self.rsim_time_step_ms / 1000.0
            self.world.rsim_n_enemies = 3  # sempre 3 inimigos no rsim (fora do campo por padrão)

        # [ENG] Inicializando os cronômetros do episódio
        self.tempo_inicio_episodio = time.time()
        self.fps_cmd_count = 0
        self.fps_last_time = time.time()

        self.rc = RefereeCommands()
        self.strategy = MainStrategy(self.world, static_entities=static_entities, AI_attacker=AI_attacker)

        # Variáveis
        self.message = None
        if self.world.simulado: self.world.rsim = True
        
        self.loopTime = 1.0 / loop_freq
        self.running = True
        self.is_physical_resetting = False
        self.ui_playing = not mainsystem  # Se tem MainSystem, começa pausado; senão, roda direto 
        self.execute = False
        self.lastupdatecount = 0
        self.tempo_repos = time.time()
        self.contagem = 0
        self.gol_a_favor = 0
        self.gol_contra = 0
        if self.world.firasim or self.world.travesim or self.world.rsim:
            self.radio = None
        else:
            self.radio = SerialRadio(control = control, debug = self.world.debug)

        if self.world.mainsystem:
            from client.client_pickle import ClientPickle
            from main_system.controller.communication.server_pickle import ServerPickle

            self.pclient = ClientPickle(port)
            self.state_server = ServerPickle(port=port + 1)

        # Interface gráfica para mostrar campos
        self.draw_uvf = draw_uvf
        # if self.draw_uvf: # uso do UVFScreen legado
        #     self.UVF_screen = UVFScreen(self.world, index_uvf_robot=1)
            # self.UVF_screen.initialiazeScreen()
            # self.UVF_screen.initialiazeObjects()

    def x(self, begin=None, end=None):
        if begin is None: begin = -self.world.field.maxX + 0.1
        if end is None: end = self.world.field.maxX - 0.1
        return random.uniform(begin, end)

    def y(self, begin=None, end=None):
        if begin is None: begin = -self.world.field.maxY + 0.1
        if end is None: end = self.world.field.maxY - 0.1
        return random.uniform(begin, end)

    def theta(self):
        return random.uniform(0, 360)

    def get_valid_positions(self, num_robots, robot_radius=0.15):
        positions = []
        ball_pos = [self.x(), self.y(), 0.0, 0.0]
        
        for _ in range(num_robots):
            valid = False
            while not valid:
                x = self.x()
                y = self.y()
                theta = self.theta()
                
                # Verify distance to ball
                if (x - ball_pos[0])**2 + (y - ball_pos[1])**2 < robot_radius**2:
                    continue
                    
                # Verify distance to other generated robots
                valid = True
                for px, py, _ in positions:
                    if (x - px)**2 + (y - py)**2 < (robot_radius * 2)**2:
                        valid = False
                        break
                        
            positions.append([x, y, theta])
            
        return ball_pos, positions


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

        # ... (restante dos turnOff e sys.exit) ...
        if self.world.firasim:
            for _ in range(3):
                self.firasim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            if shutdown:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOff()
        elif self.world.travesim:
            for _ in range(3):
                self.travesim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            if shutdown:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOff()
            
        elif self.world.rsim:
            if self.radio is not None: self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
            if shutdown:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOff()
        elif self.world.mainsystem:
            if self.world.firasim:
                for _ in range(3):
                    self.firasim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            elif self.world.travesim:
                for _ in range(3):
                    self.travesim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            if self.radio is not None: self.radio.send(self.world.n_robots, [(0,0) for robot in self.world.team])
            if shutdown:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOff()
        elif self.world.rsim:
            self.rsim.step([(0,0) for robot in self.world.team])
            if shutdown:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOff()

        if shutdown:
            import time
            time.sleep(0.5)
            sys.exit(0) #OBS, já que se foi dado ctrl+c, o programa chamará essa função e qualquer coisa que acontecerá depois não ocorrerá por causa do sys.exit(0)

    # =========================================================================
    # [UNBALL - CONTROL ENG] Gerenciamento Dinâmico do Preditor de Estado
    # =========================================================================
    def set_predictor_state(self, state: bool):
        state = bool(state)
        self.use_predictor = state
        self.vision_interceptor.set_active(state)

    def loop(self):
        if self.world.updateCount == self.lastupdatecount: return
        self.t0 = time.time()
        self.lastupdatecount = self.world.updateCount

        # Se MainSystem está ativo e UI está pausada OU se trocou de time recentemente, envia zero e pula a estratégia
        is_testing = getattr(self, "episode_testing_running", False)
        if (self.world.mainsystem and not self.ui_playing and not is_testing) or getattr(self, "team_change_cooldown", 0) > 0:
            if getattr(self.world, 'flag_debug', getattr(self.world, 'debug', False)):
                print(f"DEBUG LOOP: PAUSADO! ui_playing={self.ui_playing}, cooldown={getattr(self, 'team_change_cooldown', 0)}")
            if getattr(self, "team_change_cooldown", 0) > 0:
                self.team_change_cooldown -= 1
            if self.world.firasim:
                self.firasim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            elif self.world.travesim:
                self.travesim.command.writeMulti([(0.0, 0.0) for _ in self.world.n_robots], robot_ids=self.world.n_robots)
            # Ainda desenha e envia estado para UI
            # self.draw()
            if self.world.mainsystem:
                state_msg = {
                    "running": self.ui_playing,
                    "team_side": self.world.field.side,
                    "team_yellow": self.team_yellow,
                    "robots": {},
                    "enemies": {},
                    "episode_testing_running": getattr(self, "episode_testing_running", False)
                }
                if getattr(self, 'is_physical_resetting', False):
                    state_msg["is_physical_resetting"] = True
                
                if self.world.firasim or self.world.travesim or self.world.rsim:
                    state_msg["ball"] = {
                        "pos_x": self.world.ball.pos[0],
                        "pos_y": self.world.ball.pos[1],
                        "vel_x": self.world.ball.v[0],
                        "vel_y": self.world.ball.v[1]
                    }
                    for i in self.world.n_robots:
                        if self.world.team[i] is not None:
                            robot = self.world.team[i]
                            state_msg["robots"][str(i)] = {
                                "pos_x": robot.pos[0],
                                "pos_y": robot.pos[1],
                                "th": robot.th,
                                "dir": robot.direction
                            }
                    for i in self.world.n_robots:
                        if self.world.enemies[i] is not None:
                            robot = self.world.enemies[i]
                            state_msg["enemies"][str(i)] = {
                                "pos_x": robot.pos[0],
                                "pos_y": robot.pos[1],
                                "th": robot.th,
                                "dir": getattr(robot, "direction", 1)
                            }
                state_msg["uvf_grid"] = getattr(self, '_hlc_uvf_grid', None)
                self.state_server.send(state_msg)
            if hasattr(self, '_t_start_loop'):
                t_state = time.time()
                if t_state - self._t_start_loop > 0.01:
                    import sys
                    # print(f"\nSLOW LOOP BOTTLE: total={t_state-self._t_start_loop:.4f} | strat={getattr(self, '_t_strat', t_state)-self._t_start_loop:.4f} | actuate={getattr(self, '_t_act', t_state)-getattr(self, '_t_strat', t_state):.4f} | draw={getattr(self, '_t_draw', t_state)-getattr(self, '_t_act', t_state):.4f} | state={t_state-getattr(self, '_t_draw', t_state):.4f}", file=sys.stderr)
                del self._t_start_loop
            return



        self._t_start_loop = time.time()
        

        
        # Executa estratégia
        self.strategy.update(self.world)
        
        # --- DEBUG DE ENTIDADES (A pedido) ---
        _t_now = time.time()
        if not hasattr(self, '_last_ent_print') or _t_now - self._last_ent_print > 0.5:
            self._last_ent_print = _t_now
            ent_str = " | ".join([f"R{r.id}: {r.entity.__class__.__name__ if getattr(r, 'entity', None) else 'None'}" for r in self.world.team if r is not None])
            print(f"[ENTIDADES] {ent_str}")
        # -------------------------------------

        try:
            if getattr(self.world, 'flag_record_sim2real', False):
                # Cria a pasta data/ caso não exista
                import os
                os.makedirs("data", exist_ok=True)
                with open("data/sim2real_recorded_data.csv", "a") as f:
                    t = time.time()
                    for r_id in range(len(self.world.team)):
                        try:
                            r = self.world.team[r_id]
                            if r is not None and r.poseDefined:
                                f.write(f"{t:.4f},{r_id},{r._raw_x},{r._raw_y},{r._raw_th},{r.v_signed},{r.angvel}\n")
                        except Exception as inner_e:
                            print(f"[Loop Record Inner Error] r_id={r_id} {inner_e}")
                            with open("data/record_error.log", "a") as err_f:
                                err_f.write(f"[Inner] r_id={r_id} {inner_e}\n")
            
            with open("trajectory_kalman.csv", "a") as f:
                t = time.time()
                atacante = self.world.team[0] if self.world.team and len(self.world.team)>0 else None
                if atacante is not None and hasattr(atacante, 'raw_x'):
                    f.write(f"{t:.4f},{atacante.raw_x},{atacante.raw_y},{atacante.x},{atacante.y},{atacante.vx},{atacante.vy}\n")
        except Exception as e:
            print(f"[Loop Record Error] {e}")
            with open("data/record_error.log", "a") as err_f:
                err_f.write(f"{e}\n")
        self._t_strat = time.time()

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
        control_output = [(0, 0), (0, 0), (0, 0)]
        if self.world.mainsystem: control_output = [robot.entity.control.actuate(robot) if robot.entity else (0,0) for robot in self.world.team if robot is not None]
        self._t_act = time.time()
        if self.world.firasim: control_output = [robot.entity.control.actuateSimu(robot) if robot.entity else (0,0) for robot in self.world.team if robot is not None]
        if self.world.travesim: control_output = [robot.entity.control.actuateSimu(robot) if robot.entity else (0,0) for robot in self.world.team if robot is not None]
        if self.world.rsim:
            control_output = [robot.entity.control.actuateSimu(robot) if robot.entity else (0,0) for robot in self.world.team if robot is not None]
            # print(f"[RSIM DEBUG] control_output: {control_output}", flush=True)

        # [HLC] Controle manual: sobrepõe TODA a estratégia com v/w fixos vindos da UI,
        # convertidos para velocidades de roda no modo atual. Aplica a todos os robôs.
        if getattr(self, 'manual_control', False):
            from tools import speeds2motors
            mv = getattr(self, 'manual_v', 0.0)
            mw = getattr(self, 'manual_w', 0.0)
            n = len([r for r in self.world.team if r is not None])
            control_output = [speeds2motors(mv, mw, self.world.mode) for _ in range(n)]

        # # =====================================================================
        # # EXECUÇÃO DO CONTROLE & [ENG] LOG DE FEEDBACK DE COMANDO
        # # =====================================================================
        # if self.world.firasim:
        #     if self.execute:
        #         for robot in self.world.raw_team: 
        #             if robot is not None: robot.turnOn()   
        #         self.firasim.command.writeMulti(control_output, robot_ids=self.world.n_robots)
                
        #         # [ENG] Registrar Feedback FIRASim para integral do Preditor
        #         t_send = time.monotonic()
        #         for i, robot_id in enumerate(self.world.n_robots):
        #             if i < len(control_output): 
        #                 v_cmd, w_cmd = control_output[i]
        #                 self.cmd_logger.push(robot_id, v_cmd, w_cmd, t_send)
        if self.world.firasim:
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.firasim.command.writeMulti(control_output, robot_ids=self.world.n_robots)
                t_send = time.monotonic()
                for i, robot_id in enumerate(self.world.n_robots):
                    if i < len(control_output):
                        vl, vr = control_output[i]
                        v_cmd, w_cmd = motors2speeds_from_vl_vr(vl, vr, "firasim")
                        v_cmd_safe = max(-2.5, min(float(v_cmd), 2.5))
                        w_cmd_safe = max(-20.0, min(float(w_cmd), 20.0))
                        t_send = time.monotonic()
                        self.vision_interceptor.push_cmd(int(robot_id), float(v_cmd_safe), float(w_cmd_safe), float(t_send))
                        robot = self.world.get_raw_robot(robot_id) if hasattr(self.world, 'get_raw_robot') else self.world.team[robot_id] if robot_id < len(self.world.team) else None
                        if robot and getattr(robot, 'neural_estimator', None):
                            robot.neural_estimator.push_command(float(v_cmd_safe), float(w_cmd_safe))
        elif self.world.travesim:
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                self.travesim.command.writeMulti(control_output, robot_ids=self.world.n_robots)
                t_send = time.monotonic()
                for i, robot_id in enumerate(self.world.n_robots):
                    if i < len(control_output):
                        vl, vr = control_output[i]
                        v_cmd, w_cmd = motors2speeds_from_vl_vr(vl, vr, "travesim")
                        v_cmd_safe = max(-2.5, min(float(v_cmd), 2.5))
                        w_cmd_safe = max(-20.0, min(float(w_cmd), 20.0))
                        t_send = time.monotonic()
                        self.vision_interceptor.push_cmd(int(robot_id), float(v_cmd_safe), float(w_cmd_safe), float(t_send))
                        robot = self.world.get_raw_robot(robot_id) if hasattr(self.world, 'get_raw_robot') else self.world.team[robot_id] if robot_id < len(self.world.team) else None
                        if robot and getattr(robot, 'neural_estimator', None):
                            robot.neural_estimator.push_command(float(v_cmd_safe), float(w_cmd_safe))

        if self.world.mainsystem:   
            if self.execute:
                for robot in self.world.raw_team: 
                    if robot is not None: robot.turnOn()   
                if self.radio is not None: self.radio.send(self.world.n_robots, control_output)
                
                # [ENG] Registrar Feedback MainVision para integral do Preditor
                t_send = time.monotonic()
                for i, robot_id in enumerate(self.world.n_robots):
                    if i < len(control_output):
                        v_cmd, w_cmd = control_output[i]
                        t_send = time.monotonic()
                        self.vision_interceptor.push_cmd(robot_id, v_cmd, w_cmd, t_send)
                        robot = self.world.get_raw_robot(robot_id) if hasattr(self.world, 'get_raw_robot') else self.world.team[robot_id] if robot_id < len(self.world.team) else None
                        if robot and getattr(robot, 'neural_estimator', None):
                            robot.neural_estimator.push_command(float(v_cmd), float(w_cmd))
                        
        if self.world.rsim:
            for robot in self.world.raw_team:
                if robot is not None: robot.turnOn()
            self.control_output = control_output
            # O rsim é inicializado com 3 inimigos (passivos), então step() exige
            # comandos para os 6 robôs (3 azuis + 3 amarelos, nessa ordem). Os inimigos
            # recebem comando zero (ficam parados, atuando como barreiras físicas).
            n_enemy = getattr(self.world, 'rsim_n_enemies', 0)
            if n_enemy > 0:
                enemy_cmds = [(0.0, 0.0)] * n_enemy
                # Modo 1v1: o inimigo 0 é controlado por uma entidade (world espelhado).
                # Os demais ficam parados/fora do campo.
                if getattr(self, 'episode_enemy_entity', ''):
                    ecmd = self._compute_enemy_command()
                    if ecmd is not None and n_enemy >= 1:
                        enemy_cmds[0] = ecmd
                if self.world.team_yellow:
                    # aliados são amarelos → inimigos (azuis) vêm primeiro
                    full_output = enemy_cmds + list(control_output)
                else:
                    # aliados são azuis → vêm primeiro, inimigos (amarelos) depois
                    full_output = list(control_output) + enemy_cmds
            else:
                full_output = control_output
            # Durante o teste episódico a thread do collector chama _tick(), que repassa a chamada para o loop().
            # O loop principal é pausado (time.sleep) e não chamará loop() de forma concorrente.
            self.rsim.step(full_output)
            self.last_tB = time.time()
            if not hasattr(self, '_rsim_step_count'): self._rsim_step_count = 0
            self._rsim_step_count += 1
            if getattr(self, 'debug_prints', False) and self._rsim_step_count % 150 == 0:
                    print(f"\n[RSIM] Simulado executando passo físico {self._rsim_step_count}...", file=sys.stderr)
        if getattr(self.world, 'flag_debug', getattr(self.world, 'debug', False)):
            contador = 0
            for v1, v2 in control_output:
                print(f"DEBUG ACTUATE DO ROBO {contador} | V {v1:.2f} | W {v2:.2f}")
                contador += 1
            
        if self.world.debug and constants.DEBUG_ACTUATE:
            contador = 0
            for v1, v2 in control_output:
                print(f"ACTUATE DO ROBO {contador} | V {v1:.2f} | W {v2:.2f}")
                contador+=1

        # Desenha no ALP-GUI
        # from client.gui import clientProvider
        # clientProvider().begin_batch()
        # self.draw()
        # clientProvider().end_batch()
        self._t_draw = time.time()
        
        if self.world.mainsystem:
            state_msg = {
                "running": self.ui_playing,
                "team_side": self.world.field.side,
                "team_yellow": self.team_yellow,
                "robots": {},
                "enemies": {},
                "episode_testing_running": getattr(self, "episode_testing_running", False)
            }
            if getattr(self, 'is_physical_resetting', False):
                state_msg["is_physical_resetting"] = True

            if self.world.firasim or self.world.travesim or self.world.rsim:
                state_msg["ball"] = {
                    "pos_x": self.world.ball.pos[0],
                    "pos_y": self.world.ball.pos[1],
                    "vel_x": self.world.ball.v[0],
                    "vel_y": self.world.ball.v[1]
                }
                for i in self.world.n_robots:
                    if self.world.team[i] is not None:
                        robot = self.world.team[i]
                        state_msg["robots"][str(i)] = {
                            "pos_x": robot.pos[0],
                            "pos_y": robot.pos[1],
                            "th": robot.th,
                            "dir": robot.direction
                        }
                for i in self.world.n_robots:
                    if self.world.enemies[i] is not None:
                        robot = self.world.enemies[i]
                        state_msg["enemies"][str(i)] = {
                            "pos_x": robot.pos[0],
                            "pos_y": robot.pos[1],
                            "th": robot.th,
                            "dir": getattr(robot, "direction", 1)
                        }
            state_msg["uvf_grid"] = getattr(self, '_hlc_uvf_grid', None)
            self.state_server.send(state_msg)
            if hasattr(self, '_t_start_loop'):
                t_state = time.time()
                if t_state - self._t_start_loop > 0.01:
                    del self._t_start_loop

    def busyLoop(self):
        # Tenta ler pacotes UDP de configuração enviados pela UI
        try:
            data, _ = self.noise_config_sock.recvfrom(4096)
            import json
            new_cfg = json.loads(data.decode('utf-8'))
            self.vision_noise_simulator.update_config(new_cfg)
        except Exception:
            pass

        if self.world.firasim or self.world.travesim:
            # 1. Lê os pacotes da rede O MAIS RÁPIDO POSSÍVEL (sem sleep!)
            sim_client = self.firasim if self.world.firasim else self.travesim
            messages = sim_client.vision.read()
            
            if messages:
                if isinstance(messages, list):
                    for msg in messages:
                        self.vision_interceptor.enqueue_frame(msg)
                else:
                    self.vision_interceptor.enqueue_frame(messages)

            self.execute = False

            # 2. Processa todas as mensagens que já passaram da "idade" do nosso delay
            if hasattr(self.vision_interceptor, 'dequeue_ready_frames'):
                ready_frames = self.vision_interceptor.dequeue_ready_frames()
            else:
                rf = self.vision_interceptor.dequeue_ready_frame()
                ready_frames = [rf] if rf is not None else []
                
            if ready_frames:
                t_oldest, oldest_msg = ready_frames[-1]
                self.message = oldest_msg
                self.execute = True
                
                # Mas analisamos todos para não perder eventos transient (ex: bola entra e sai do gol)
                for t_frame, msg in ready_frames:
                    if hasattr(msg, 'frame') and hasattr(msg.frame, 'ball'):
                        # Ajeita a cordenada x (side)
                        bx = msg.frame.ball.x * self.world.field.side
                        by = msg.frame.ball.y
                        if bx > self.world.field.maxX and abs(by) < self.world.field.goalAreaHeight/2:
                            self.world.transient_goal_aliado = True
                        elif bx < -self.world.field.maxX and abs(by) < self.world.field.goalAreaHeight/2:
                            self.world.transient_goal_inimigo = True

            if getattr(self, 'execute', False):
                if ready_frames:
                    # Intercepta e prediz (muta o pacote) APENAS SE FOR NOVO
                    if getattr(self.world, "flag_use_vision_noise", False):
                        if self.vision_noise_simulator.config.get('domain_randomization_enabled', False):
                            self.noise_frame_counter += 1
                            if self.noise_frame_counter >= self.vision_noise_simulator.config.get('domain_randomization_interval', 5000):
                                self.vision_noise_simulator.randomize_domain()
                                self.noise_frame_counter = 0
                        self.vision_noise_simulator.apply_noise(self.message)
                    
                    self.vision_interceptor.intercept_and_predict(
                        message=self.message, 
                        t_frame=t_oldest, 
                        team_yellow=self.team_yellow, 
                        n_robots=self.world.n_robots, 
                        alpha=1.0
                    )
                
                # O UnBrain agora chamará internamente os métodos .updateSimu() com dados corretos!
                self.world.FIRASim_update(self.message)

        if getattr(self.world, 'vssvision', False):
            message = getattr(self, 'visionclient', None)
            if message is not None:
                message = self.visionclient.receive_frame()
            if message:
                self.vision_interceptor.enqueue_frame(message)
                
            self.execute = False
            frame_data = self.vision_interceptor.dequeue_ready_frame()
            if frame_data is not None:
                t_oldest, oldest_msg = frame_data
                self.message = oldest_msg
                self.execute = True
                
                if getattr(self.world, "flag_use_vision_noise", False):
                    if self.vision_noise_simulator.config.get('domain_randomization_enabled', False):
                        self.noise_frame_counter += 1
                        if self.noise_frame_counter >= self.vision_noise_simulator.config.get('domain_randomization_interval', 5000):
                            self.vision_noise_simulator.randomize_domain()
                            self.noise_frame_counter = 0
                    self.vision_noise_simulator.apply_noise(self.message)
                
                self.vision_interceptor.intercept_and_predict(
                    message=self.message, 
                    t_frame=t_oldest, 
                    team_yellow=self.team_yellow, 
                    n_robots=self.world.n_robots, 
                    alpha=1.0
                )
                
                self.world.delay_camera = time.time()
                self.world.VSSVision_update(self.message.detection)

        if self.world.mainsystem:
            try:
                message = self.pclient.receive()
                if message is not None:
                    if "running" in message:
                        new_running = message["running"]
                        if self.ui_playing != new_running:
                            if not new_running:
                                self.handle_SIGINT(0, 0, shutdown=False)
                            self.ui_playing = new_running

                    # [HLC] Controle manual: sobrepõe a estratégia enviando v/w fixos aos robôs.
                    if "manual_control" in message:
                        self.manual_control = bool(message["manual_control"])
                        self.manual_v = float(message.get("manualControlSpeedV", 0.0))
                        self.manual_w = float(message.get("manualControlSpeedW", 0.0))
                    
                    if "team_yellow" in message:
                        if self.team_yellow != message["team_yellow"]:
                            self.handle_SIGINT(0, 0, shutdown=False)
                            self.team_yellow = message["team_yellow"]
                            self.world.team_yellow = self.team_yellow
                            self.team_change_cooldown = 120 # Congele a velocidade por cerca de 0.5s-1s para os filtros se adaptarem
                            if self.world.firasim:
                                self.firasim.command.team_yellow = self.team_yellow
                            if self.world.travesim:
                                self.travesim.command.team_yellow = self.team_yellow
                                
                    # [ENG] Novas Flags Dinâmicas
                    if "use_predictor" in message:
                        if self.use_predictor != message["use_predictor"]:
                            self.set_predictor_state(message["use_predictor"])
                            
                    if "disable_ai" in message:
                        self.world.disable_ai = message["disable_ai"]
                        self.vision_interceptor.disable_ai = message["disable_ai"]
                        
                    if "teleport_mode" in message and not getattr(self, "episode_testing_running", False):
                        self.world.teleport_mode = message["teleport_mode"]
                    if "teleport_config" in message and not getattr(self, "episode_testing_running", False):
                        self.world.teleport_config = message["teleport_config"]

                    # Executa teleporte imediato do simulador
                    if "teleport_mode_enemy" in message and message["teleport_mode_enemy"] is not None and not getattr(self, "episode_testing_running", False):
                        if self.world.firasim or self.world.travesim:
                            sim_client = self.firasim if self.world.firasim else self.travesim
                            config_enemy = message["teleport_config"].get(message["teleport_mode_enemy"], {})
                            for i in range(3):
                                if i in config_enemy or str(i) in config_enemy:
                                    pos = config_enemy.get(str(i), config_enemy.get(i))
                                    sim_client.command.setPos(i, pos['x'], pos['y'], pos['th'], is_enemy=True)

                    if "teleport_ball_pos" in message and message["teleport_ball_pos"] is not None:
                        if self.world.firasim or self.world.travesim:
                            sim_client = self.firasim if self.world.firasim else self.travesim
                            bx, by = message["teleport_ball_pos"]
                            sim_client.command.setBallPos(bx, by)

                    if "flags" in message:
                        flags = message["flags"]
                        
                        # Process referee
                        if "referee" in flags:
                            self.world.flag_referee = flags["referee"]
                            self.world.referee = flags["referee"]
                        
                        # Process control tester
                        if "control" in flags:
                            self.world.flag_control_tester = flags["control"]
                        if "test_roles" in flags:
                            self.world.test_roles = flags["test_roles"]
                        
                        # Process other global flags
                        if "debug" in flags:
                            self.world.flag_debug = flags["debug"]
                            self.world.debug = flags["debug"]
                            if getattr(self, "radio", None) is not None:
                                self.radio.debug = flags["debug"]
                        if "ppo_ai" in flags:
                            if getattr(self.world, "flag_ppo_ai", False) != flags["ppo_ai"]:
                                self.world.flag_ppo_ai = flags["ppo_ai"]
                                print(f"====> [DEBUG UI] Reinforcement Learning (PPO AI) {'ATIVADO' if flags['ppo_ai'] else 'DESATIVADO'} <====")
                        if "enemy_ai" in flags:
                            self.world.flag_enemy_ai = flags["enemy_ai"]
                        if "record" in flags:
                            self.world.flag_record = flags["record"]
                            if getattr(self, "vision_interceptor", None) is not None:
                                self.vision_interceptor.set_record_state(flags["record"])
                        if "static_entities" in flags:
                            self.world.flag_static_entities = flags["static_entities"]
                        if "force_entities" in flags:
                            self.world.force_entities = flags["force_entities"]
                        # [HLC] Robô cujo campo vetorial deve ser amostrado para o overlay
                        # (-1 = desligado). Liga/desliga a thread amostradora sem custo no loop.
                        if "hlc_show_field" in flags:
                            self._hlc_show_field = int(flags["hlc_show_field"])
                        if "use_kalman" in flags:
                            if getattr(self.world, "flag_use_kalman", False) != flags["use_kalman"]:
                                self.world.flag_use_kalman = flags["use_kalman"]
                                print(f"====> [DEBUG UI] Filtro de Kalman {'ATIVADO' if flags['use_kalman'] else 'DESATIVADO'} <====")
                                if flags["use_kalman"]:
                                    self.world.ball.poseDefined = False
                                    for r in self.world.team + self.world.enemies:
                                        r.poseDefined = False
                        if "use_neural_estimator" in flags:
                            if getattr(self.world, "flag_use_neural_estimator", False) != flags["use_neural_estimator"]:
                                self.world.flag_use_neural_estimator = flags["use_neural_estimator"]
                                print(f"====> [DEBUG UI] Neural Estimator (Deep Learning) {'ATIVADO' if flags['use_neural_estimator'] else 'DESATIVADO'} <====")
                        if "use_vision_noise" in flags:
                            if getattr(self.world, "flag_use_vision_noise", False) != flags["use_vision_noise"]:
                                self.world.flag_use_vision_noise = flags["use_vision_noise"]
                        if "record_sim2real" in flags:
                            if flags["record_sim2real"] and not getattr(self.world, "flag_record_sim2real", False):
                                if _test_type == "heatmap_attacker_ia":
                                    self.world = World(n_robots=[robot_id], side=1, team_yellow=False, rsim=True, AI_attacker=True, enemy_AI=True, simulado=True)
                                # Começou a gravar
                                self.world.flag_record_sim2real = True
                                print("====> [DEBUG UI] GRAVAÇÃO SIM2REAL INICIADA: A gravar física do FiraSim/TraveSim para dataset! <====")
                            elif not flags["record_sim2real"] and getattr(self.world, "flag_record_sim2real", False):
                                # Parou de gravar
                                self.world.flag_record_sim2real = False
                                print("====> [DEBUG UI] GRAVAÇÃO SIM2REAL PARADA! <====")
                        if "mirror" in flags:
                            self.world.flag_mirror = flags["mirror"]
                            self.world.mirror = flags["mirror"]
                            self.world.field.side = -1 if flags["mirror"] else 1
                        if "use_predictor" in flags:
                            self.world.flag_use_predictor = flags["use_predictor"]
                            if getattr(self, "use_predictor", False) != flags["use_predictor"]:
                                self.set_predictor_state(flags["use_predictor"])
                        if "disable_ai" in flags:
                            self.world.flag_disable_ai = flags["disable_ai"]
                            self.world.disable_ai = flags["disable_ai"]
                            if getattr(self, "vision_interceptor", None):
                                self.vision_interceptor.disable_ai = flags["disable_ai"]
                        if "n_robots" in flags:
                            try:
                                if isinstance(flags["n_robots"], list):
                                    new_n_robots = [int(e) for e in flags["n_robots"]]
                                else:
                                    new_n_robots = [int(e) for e in flags["n_robots"].split(",")]
                                    
                                if self.world.n_robots != new_n_robots:
                                    self.world.n_robots = new_n_robots
                                    self.n_robots = new_n_robots
                                    
                                    from world.elements import TeamRobot
                                    self.world._team = [None, None, None]
                                    self.world.enemies = [None, None, None]
                                    for i in self.world.n_robots:
                                        self.world._team[i] = TeamRobot(self.world, i, on=True)
                                        self.world.enemies[i] = TeamRobot(self.world, i, on=True)
                                        self.world.enemies[i].xvec.add(1000000000000000)
                                        
                                    from strategy import Strategy
                                    self.strategy = Strategy(self.world, [r for r in self.world.team if r is not None])
                            except Exception as e:
                                print(f"Error hot-swapping n_robots: {e}")
                        
                        # [ENG] Episode Testing UI Coupling
                        if "episode_test_run" in flags:
                            run_flag = flags["episode_test_run"]
                            # Latch: só inicia UMA vez por clique. A flag da UI continua True
                            # enquanto o botão está pressionado; sem o latch, o loop relançaria
                            # o teste a cada ciclo IPC assim que o anterior terminasse (gerando
                            # heatmaps infinitos). O latch só reseta quando a flag volta a False.
                            if run_flag and not getattr(self, "episode_testing_running", False) \
                                    and not getattr(self, "_episode_run_consumed", False):
                                self._episode_run_consumed = True
                                seed       = flags.get("episode_test_seed", 0)
                                max_steps  = flags.get("episode_test_max_steps", 1200)
                                n_episodes = flags.get("episode_test_n_episodes", 1)
                                n_enemies  = flags.get("episode_test_n_enemies", 0)
                                enemy_entity = flags.get("episode_test_enemy_entity", "")
                                test_type  = flags.get("episode_test_type", "heatmap_team")
                                is_fixed   = flags.get("episode_test_is_fixed", True)
                                if test_type:
                                    self.test_type = test_type
                                print(f"====> [DEBUG UI] Inciando Teste Episódico (Seed: {seed}, Steps: {max_steps}, Eps: {n_episodes}, Type: {self.test_type}, Inimigos: {n_enemies}, Entidade inimiga: '{enemy_entity}', Fixed: {is_fixed}) <====", flush=True)
                                self.start_episode_test_thread(seed, max_steps, n_episodes, n_enemies=n_enemies, enemy_entity=enemy_entity, is_fixed=is_fixed)
                            # Flag baixou (botão solto/auto-cancelado): libera o latch e para se preciso.
                            elif not run_flag:
                                self._episode_run_consumed = False
                                if getattr(self, "episode_testing_running", False):
                                    print(f"====> [DEBUG UI] Parando Teste Episódico <====", flush=True)
                                    self.stop_episode_test()

                    if "global_control_params" in message:
                        for control_name, params in message["global_control_params"].items():
                            for robot in self.world.team:
                                if robot is not None and robot.entity and hasattr(robot.entity, 'control') and robot.entity.control is not None:
                                    if robot.entity.control.__class__.__name__ == control_name:
                                        for k, v in params.items():
                                            if hasattr(robot.entity.control, k):
                                                if getattr(robot.entity.control, k) != v:
                                                    setattr(robot.entity.control, k, v)

                    # [HLC] Override de parâmetros do UVF vindo da interface (só os que
                    # o usuário editou; dict vazio mantém os valores do artigo).
                    if "hlc_uvf_overrides" in message:
                        self.world.hlc_uvf_overrides = message["hlc_uvf_overrides"] or {}
                        
                    # Se não estiver rodando FiraSim/TraveSim/VSSVision, usa a mensagem como frame de visão
                    if not (self.world.firasim or self.world.travesim or self.world.rsim):
                        if self.ui_playing:
                            self.vision_interceptor.enqueue_frame(message)
            except ConnectionError:
                self.handle_SIGINT(0,0, shutdown=True)
            
            # Só faz dequeue/execute aqui se NÃO houver simulador de visão (senão o bloco acima já fez)
            if not (self.world.firasim or self.world.travesim or self.world.rsim):
                self.execute = False
                frame_data = self.vision_interceptor.dequeue_ready_frame()
                if frame_data is not None:
                    t_oldest, oldest_msg = frame_data
                    self.message = oldest_msg
                    self.execute = True
                    
                if getattr(self.world, "flag_use_vision_noise", False):
                    if self.vision_noise_simulator.config.get('domain_randomization_enabled', False):
                        self.noise_frame_counter += 1
                        if self.noise_frame_counter >= self.vision_noise_simulator.config.get('domain_randomization_interval', 5000):
                            self.vision_noise_simulator.randomize_domain()
                            self.noise_frame_counter = 0
                    self.vision_noise_simulator.apply_noise(self.message)
                    self.vision_interceptor.intercept_and_predict(
                        message=self.message, 
                        t_frame=t_oldest, 
                        team_yellow=self.team_yellow, 
                        n_robots=self.world.n_robots, 
                        alpha=1.0
                    )
                    
                    self.world.update_main_vision(self.message)

        if self.world.rsim:
            message = self.rsim.get_state()
            self.message = message if message else self.message
            self.execute = True if self.message else False
            # print(f"[DEBUG RSIM STATE] message length: {len(message) if message else 0}, execute: {self.execute}")
            if self.execute:
                self.world.update(self.message)
            self.world.execute = self.execute
        
        elif(self.world.debug and not (self.world.rsim) and not (self.world.firasim) and not (self.world.travesim) and not self.world.mainsystem and not self.world.rsim):
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

        if self.execute and getattr(self, 'use_predictor', False):
            for i in self.world.n_robots:
                # Team
                if self.world.team[i] is not None:
                    raw = self.vision_interceptor.get_raw_pose(self.team_yellow, i)
                    if raw:
                        self.world.team[i].raw_x = raw[0]
                        self.world.team[i].raw_y = raw[1]
                        self.world.team[i].raw_th = raw[2]
                # Enemies
                if self.world.enemies[i] is not None:
                    raw = self.vision_interceptor.get_raw_pose(not self.team_yellow, i)
                    if raw:
                        self.world.enemies[i].raw_x = raw[0]
                        self.world.enemies[i].raw_y = raw[1]
                        self.world.enemies[i].raw_th = raw[2]

    def reset_firasim_episode(self):
        """Teletransporta a bola e robôs no FIRASim para iniciar novo episódio limpo"""
        if self.world.firasim and hasattr(self, 'firasim'):
            sim_client = self.firasim
        elif self.world.travesim and hasattr(self, 'travesim'):
            sim_client = self.travesim
        else:
            return

        # 1. Posições aleatórias para a bola (Centro do campo, variando levemente)
        bx = random.uniform(-0.1, 0.1)
        by = random.uniform(-0.3, 0.3)
        sim_client.command.setBallPos(bx, by)
        
        # 2. Reposiciona os Robôs para o campo de defesa!
        if len(self.n_robots) > 0:
            ry_0 = random.uniform(-0.1, 0.1)
            sim_client.command.setPos(self.n_robots[0], -0.3, ry_0, 0.0)
            
        if len(self.n_robots) > 1:
            sim_client.command.setPos(self.n_robots[1], -0.6, 0.15, 0.0)
            
        if len(self.n_robots) > 2:
            sim_client.command.setPos(self.n_robots[2], -0.6, -0.15, 0.0)
            
        # 3. Reseta cronômetros e histórico de stuck ball para não carregar lixo da jogada anterior
        self.tempo_inicio_episodio = time.time()
        self.last_ball_x.clear()
        self.last_ball_y.clear()

    def draw(self):
        for robot in [r for r in self.world.team if r is not None]:
            clientProvider().drawRobot(robot.id, robot.x, robot.y, robot.th, robot.direction)
            
            # [ENG] Visualização do StatePredictor
            # Se o preditor está ligado, desenhamos a "sombra" fantasma mostrando a posição crua (sem predição)
            if getattr(self, 'use_predictor', False) and hasattr(robot, 'raw_x'):
                # ID + 10 para não colidir com o ID real, cor azul claro para indicar 'fantasma' (raw vision)
                clientProvider().drawRobot(robot.id + 10, robot.raw_x, robot.raw_y, robot.raw_th, robot.direction, (0.4, 0.8, 1.0))

        for robot in [r for r in self.world.enemies if r is not None]:
            clientProvider().drawRobot(robot.id+3, robot.x, robot.y, robot.th, 1, (0.6, 0.6, 0.6))

        clientProvider().drawBall(0, self.world.ball.x, self.world.ball.y)

    def websocket_thread(self):
        from client.websocket import WebSocket
        print("entrou no ws")
        webapp = WebSocket(loop=self)
        webapp.run()

    def _start_hlc_field_sampler(self):
        """Inicia (uma vez) a thread que amostra o campo vetorial do robô selecionado."""
        if getattr(self, '_hlc_sampler_thread', None) is not None:
            return
        if not hasattr(self, '_hlc_show_field'):
            self._hlc_show_field = -1
        self._hlc_uvf_grid = None
        self._hlc_sampler_stop = False
        self._hlc_sampler_thread = threading.Thread(target=self._hlc_field_sampler, daemon=True)
        self._hlc_sampler_thread.start()

    def _hlc_field_sampler(self):
        """[Thread separada, ~10 Hz] Amostra field.F numa grade grossa 12x9 para o robô
        escolhido em self._hlc_show_field (-1 = desligado). Guarda em self._hlc_uvf_grid.
        Roda FORA do loop de controle: seu custo (~12 ms/frame p/ 300 setas) nunca afeta
        a estratégia (thread separada, ~11% de 1 núcleo @10Hz)."""
        NX, NY = 20, 15
        while not getattr(self, '_hlc_sampler_stop', False):
            idx = getattr(self, '_hlc_show_field', -1)
            grid = None
            if idx is not None and idx >= 0:
                try:
                    team = self.world.team
                    robot = team[idx] if idx < len(team) else None
                    field = getattr(robot, 'field', None) if robot is not None else None
                    if field is not None:
                        maxX = self.world.field.maxX
                        maxY = self.world.field.maxY
                        xs = np.linspace(-maxX, maxX, NX)
                        ys = np.linspace(-maxY, maxY, NY)
                        angles = []
                        for y in ys:
                            for x in xs:
                                P = np.array([x, y, 0.0])
                                try:
                                    # probe=True: parede/obstáculos relativos ao ponto amostrado
                                    # (só o UVF aceita; outros campos caem no fallback).
                                    try:
                                        angles.append(float(field.F(P, probe=True)))
                                    except TypeError:
                                        angles.append(float(field.F(P)))
                                except Exception:
                                    angles.append(0.0)
                        grid = {
                            "robot": idx, "nx": NX, "ny": NY,
                            "minx": -maxX, "maxx": maxX, "miny": -maxY, "maxy": maxY,
                            "angles": angles, "ts": time.time()
                        }
                except Exception:
                    grid = None
            self._hlc_uvf_grid = grid
            time.sleep(0.1)  # ~10 Hz

    def run_loop(self):
        t0 = 0
        tempo_zero = time.time()
        logging.info("System is running")

        # [HLC] Amostrador do campo vetorial em thread separada (~10 Hz), desacoplado
        # do loop de controle — nunca entra no caminho crítico da estratégia.
        self._start_hlc_field_sampler()

        firasim_ab_test = (self.test_type == "firasim_ab")
        intervalo_ab = 15 # 60 segundos avaliando cada modo

        # [TELEPORT] O código de teleporte foi migrado para dentro do busyLoop e do update da estratégia

        while self.running:
            now_time = time.time()
            tempo_decorrido_global = now_time - tempo_zero
            tempo_decorrido = now_time - self.tempo_inicio_episodio

            # =================================================================
            # RASTREAMENTO DO TESTE A/B (PREDITOR vs RAW) - Apenas se usar FiraSim
            if self.test_type == "firasim_ab" and (self.world.firasim or self.world.travesim) and hasattr(self, 'metrics') and hasattr(self, 'tempo_inicio_episodio'):
                novo_estado = (int(tempo_decorrido_global / intervalo_ab) % 2) == 1
                # Checa a flag correta. Se mudou, usa a função segura para recriar tudo!
                if novo_estado != self.use_predictor:
                    
                    # === RELATÓRIO DO MODO ANTERIOR ===
                    print(f"\n==================================================")
                    print(f"📈 RESULTADOS DO MODO: {self.current_mode}")
                    print(f" Gols a favor: {self.metrics[self.current_mode]['gols_aliados']}")
                    print(f" Gols contra:  {self.metrics[self.current_mode]['gols_inimigos']}")
                    stuck_count = len(self.metrics[self.current_mode]['stuck_ball'])
                    print(f" Stuck balls:  {stuck_count}")
                    
                    if self.use_predictor and self.vision_interceptor.mse_count > 0:
                        mse = self.vision_interceptor.mse_sum / self.vision_interceptor.mse_count
                        print(f" MSE Posicional (Predição vs Visão): {mse:.6f} m^2")
                    print(f"==================================================\n")
                    
                    # Reseta o acumulador de MSE
                    self.vision_interceptor.mse_sum = 0.0
                    self.vision_interceptor.mse_count = 0

                    self.set_predictor_state(novo_estado)
                    self.current_mode = "B_PRED" if self.use_predictor else "A_RAW"
                    print(f"\n[🔄 CHAVEAMENTO] Mudando para o modo: {self.current_mode}")
                    
                    self.reset_firasim_episode()
            
            if (self.world.firasim or self.world.travesim) and tempo_decorrido > 1.0 \
                    and not getattr(self, 'is_physical_resetting', False) \
                    and not getattr(self, 'episode_testing_running', False):
                is_stuck = False
                is_goal_ally = False
                is_goal_enemy = False

                # 1. Verifica STUCK BALL
                if tempo_decorrido > 5.0 and hasattr(self.world, 'ball'):
                    self.last_ball_x.append(self.world.ball.x)
                    self.last_ball_y.append(self.world.ball.y)
                    if len(self.last_ball_x) > 30:
                        self.last_ball_x.pop(0)
                        self.last_ball_y.pop(0)
                        if np.std(self.last_ball_x) < 1e-3 and np.std(self.last_ball_y) < 1e-3:
                            is_stuck = True

                if hasattr(self.world, 'ball'):
                    goal_status = self.world.field.insideGoalNet((self.world.ball.x, self.world.ball.y))
                    if goal_status == "ally_goal":
                        is_goal_ally = True
                    elif goal_status == "enemy_goal":
                        is_goal_enemy = True

                if is_stuck or is_goal_ally or is_goal_enemy:
                    if self.test_type == "firasim_ab":
                        if is_stuck:
                            print(f">>> [{self.current_mode}] STUCK BALL DETECTADO! (Tempo: {tempo_decorrido:.2f}s) Reiniciando...")
                            self.metrics[self.current_mode]["stuck_ball"].append(tempo_decorrido)
                        elif is_goal_ally:
                            print(f">>> [{self.current_mode}] GOL ALIADO! Tempo: {tempo_decorrido:.2f}s")
                            self.metrics[self.current_mode]["gols_aliados"] += 1
                            self.metrics[self.current_mode]["tempos_gol"].append(tempo_decorrido)
                        elif is_goal_enemy:
                            print(f">>> [{self.current_mode}] GOL INIMIGO! Tempo: {tempo_decorrido:.2f}s")
                            self.metrics[self.current_mode]["gols_inimigos"] += 1
                        self.reset_firasim_episode()
                    else:
                        if is_stuck:
                            event = "STUCK BALL"
                        elif is_goal_ally:
                            event = "GOL ALIADO"
                        else:
                            event = "GOL INIMIGO"
                        
                        print(f"\n[SIMULADOR] {event} detectado. Bola ao centro e robôs conduzidos via teleport.py...", file=sys.stderr)
                        sim_client = self.firasim if self.world.firasim else self.travesim

                        # 1. Teleporte estrito da bola para o centro (zera a inércia)
                        bx = random.uniform(-0.1, 0.1)
                        by = random.uniform(-0.3, 0.3)
                        sim_client.command.setBallPos(bx, by)
                        self.last_ball_x.clear()
                        self.last_ball_y.clear()

                        # 2. Conduz os robôs até a formação de reset usando o MESMO
                        #    mecanismo de teleporte da estratégia (TeleportEntity/teleport.py),
                        #    em vez de um setPos instantâneo. Enquanto teleport_mode estiver
                        #    ativo, strategy.update() assume o controle e conduz cada robô ao
                        #    alvo mais próximo, sem sobrescrever a entidade com roles normais.
                        reset_targets = [
                            {'x': -0.3, 'y': random.uniform(-0.1, 0.1), 'th': 0.0},
                            {'x': -0.6, 'y': 0.15, 'th': 0.0},
                            {'x': -0.6, 'y': -0.15, 'th': 0.0},
                        ][:len(self.world.n_robots)]
                        self.world.teleport_config["_episode_reset"] = reset_targets
                        self.world.teleport_mode = "_episode_reset"
                        self.is_physical_resetting = True
                        self.physical_reset_start_time = time.time()

                        # Atualizamos o tempo de episódio para não detectar novamente no frame seguinte
                        self.tempo_inicio_episodio = time.time()

            # Máquina de estados do reset via teleport.py no FIRASim/TraveSim:
            # espera os robôs (conduzidos pela estratégia em TeleportEntity) chegarem
            # aos alvos e então devolve o controle normal, limpando o teleport_mode.
            if (self.world.firasim or self.world.travesim) and getattr(self, 'is_physical_resetting', False) \
                    and not getattr(self, 'episode_testing_running', False):
                from strategy.entity.teleport import TeleportEntity
                all_arrived = True
                any_teleporting = False
                for robot in self.world.team:
                    if robot is None: continue
                    if isinstance(getattr(robot, 'entity', None), TeleportEntity):
                        any_teleporting = True
                        dist = np.hypot(robot.x - robot.entity.target_x, robot.y - robot.entity.target_y)
                        if dist > 0.1:
                            all_arrived = False
                            break

                # Fail-safe: se após 5s os robôs não chegaram (ou a estratégia sequer
                # atribuiu as TeleportEntity, ex.: UI pausada), força o teleporte via setPos.
                tempo_reset = time.time() - getattr(self, 'physical_reset_start_time', time.time())
                if (not any_teleporting or not all_arrived) and tempo_reset > 5.0:
                    print("[Watchdog] Reset FIRASim/TraveSim falhou (Timeout). Forçando teleporte via setPos!", file=sys.stderr)
                    sim_client = self.firasim if self.world.firasim else self.travesim
                    targets = list(self.world.teleport_config.get("_episode_reset", []))
                    for robot in self.world.team:
                        if robot is None: continue
                        if isinstance(getattr(robot, 'entity', None), TeleportEntity):
                            sim_client.command.setPos(robot.id, robot.entity.target_x, robot.entity.target_y, robot.entity.target_th)
                        elif targets:
                            t = targets[robot.id] if robot.id < len(targets) else targets[0]
                            sim_client.command.setPos(robot.id, t['x'], t['y'], t['th'])
                    all_arrived = True
                    any_teleporting = True

                if any_teleporting and all_arrived:
                    print("É AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
                    self.world.teleport_mode = None
                    self.world.teleport_config.pop("_episode_reset", None)
                    self.is_physical_resetting = False
                    self.tempo_inicio_episodio = time.time()
                    self.last_ball_x.clear()
                    self.last_ball_y.clear()
                    for robot in self.world.team:
                        if robot is None: continue
                        robot.vref = 0

            if self.world.rsim == True and not self.test_type:
                trigger = None
                if time.time() - self.tempo_repos > 30:
                    trigger = 'timeout'
                    self.tempo_repos = time.time()
                    self.contagem += 1
                elif self.world.ball.x > self.world.field.goalPos[0]:
                    trigger = 'goal_ally'
                    self.tempo_repos = time.time()
                    self.contagem += 1
                    self.gol_a_favor += 1
                elif self.world.ball.x < -self.world.field.goalPos[0]:
                    trigger = 'goal_enemy'
                    self.tempo_repos = time.time()
                    self.contagem += 1
                    self.gol_contra += 1

                if trigger is not None and not getattr(self, 'is_physical_resetting', False):
                    self.is_physical_resetting = True
                    self.physical_reset_start_time = time.time()  # [Fail-Safe] Start watchdog timer
                    ball_pos, pos_robots = self.get_valid_positions(len(self.world.n_robots))
                    
                    # 1. Teleporte estrito da Bola (Zera a inércia, pois v_x=0, v_y=0)
                    # Mantém os robôs nas suas posições originais para permitir a condução cinemática
                    current_pos_robots = [[r.x, r.y, r.th] for r in self.world.team if r is not None]
                    # O rsim foi init com rsim_n_enemies inimigos; o reset precisa passar a
                    # MESMA quantidade (fora do campo), senão o motor C++ crasha (segfault).
                    n_enemy = getattr(self.world, 'rsim_n_enemies', 0)
                    enemy_pos = [[0.0, 2.0 + i * 0.2, 0.0] for i in range(n_enemy)]
                    if getattr(self, 'team_yellow', False):
                        self.rsim.reset(ball_pos, enemy_pos, current_pos_robots)
                    else:
                        self.rsim.reset(ball_pos, current_pos_robots, enemy_pos)
                    
                    # 2. Greedy Assignment
                    from strategy.entity.teleport import TeleportEntity
                    available_targets = list(pos_robots)
                    
                    for robot in self.world.team:
                        if robot is None: continue
                        if not hasattr(robot, 'original_entity'):
                            robot.original_entity = robot.entity
                            
                        best_idx = 0
                        best_dist = float('inf')
                        for idx, target in enumerate(available_targets):
                            dist = np.hypot(robot.x - target[0], robot.y - target[1])
                            if dist < best_dist:
                                best_dist = dist
                                best_idx = idx
                                
                        target_x, target_y, target_th = available_targets.pop(best_idx)
                        robot.entity = TeleportEntity(self.world, robot, target_x, target_y, target_th)
                        robot.vref = 999

                # Máquina de estados: Verifica se a recolocação foi concluída
                if getattr(self, 'is_physical_resetting', False):
                    from strategy.entity.teleport import TeleportEntity
                    all_arrived = True
                    for robot in self.world.team:
                        if robot is None: continue
                        if isinstance(robot.entity, TeleportEntity):
                            dist = np.hypot(robot.x - robot.entity.target_x, robot.y - robot.entity.target_y)
                            if dist > 0.1:
                                all_arrived = False
                                break
                    
                    # [Fail-Safe] Verifica o Watchdog (timeout > 5.0s)
                    tempo_decorrido = time.time() - getattr(self, 'physical_reset_start_time', time.time())
                    if not all_arrived and tempo_decorrido > 5.0:
                        print("[Watchdog] Auto-Physical Reset falhou (Timeout). A forçar o teleporte de emergência!")
                        # Prepara as posições de fallback para soltar os robôs
                        target_pos_robots = []
                        for robot in self.world.team:
                            if robot is not None and isinstance(getattr(robot, 'entity', None), TeleportEntity):
                                target_pos_robots.append([robot.entity.target_x, robot.entity.target_y, robot.entity.target_th])
                            elif robot is not None:
                                target_pos_robots.append([robot.x, robot.y, robot.th])
                        
                        ball_pos = [self.world.ball.x, self.world.ball.y, 0.0, 0.0]
                        n_enemy = getattr(self.world, 'rsim_n_enemies', 0)
                        enemy_pos = [[0.0, 2.0 + i * 0.2, 0.0] for i in range(n_enemy)]
                        if getattr(self, 'team_yellow', False):
                            self.rsim.reset(ball_pos, enemy_pos, target_pos_robots)
                        else:
                            self.rsim.reset(ball_pos, target_pos_robots, enemy_pos)
                        all_arrived = True  # Força a limpeza das flags

                    if all_arrived:
                        self.is_physical_resetting = False
                        self.tempo_repos = time.time()
                        self.tempo_inicio_episodio = time.time()
                        self.last_ball_x.clear()
                        self.last_ball_y.clear()
                        
                        for robot in self.world.team:
                            if robot is None: continue
                            robot.vref = 0
                            if hasattr(robot, 'original_entity'):
                                robot.entity = robot.original_entity
                                del robot.original_entity
                
                if self.contagem == 100:
                    self.contagem = 0
                    self.gol_a_favor = 0
                    self.gol_contra = 0
            
            # if getattr(self.world, 'travesim', False) or getattr(self.world, 'firasim', False) or getattr(self.world, 'rsim', False):
            #     self.loopTime = 1.0 / 200.0
            # else:
            #     self.loopTime = self.loopTime

            # Start of cycle
            if getattr(self, 'episode_testing_running', False):
                time.sleep(0.05)
                continue
            
            t0 = time.time()

            # Execute vision and referee network handlers
            self.busyLoop()
            
            # Execute strategic loop
            self.loop()

            # Calculate how long the work took
            work_time = time.time() - t0
            tempo_restante = self.loopTime - work_time
            
            # Yield CPU if we finished early
            if tempo_restante > 0:
                # print(f'\ntime.sleep = {self.loopTime - work_time}')
                # print(f'\ntempo restante = {tempo_restante}')
                time.sleep(tempo_restante-0.0001 if tempo_restante > 0.0001 else tempo_restante)
                
            # True execution time of the full cycle
            self.world.execTime = time.time() - t0

            flags_status = []
            visible_flags = []
            for k, name in [
                ('flag_referee', 'REF'), 
                ('flag_control', 'CTRL'), 
                ('flag_debug', 'DBG'), 
                ('flag_ppo_ai', 'PPO'), 
                ('flag_enemy_ai', 'ENM'), 
                ('flag_record', 'REC'), 
                ('flag_static_entities', 'STAT'),
                ('flag_mirror', 'MIRR'),
                ('flag_use_kalman', 'KLM'),
                ('flag_use_neural_estimator', 'NRE')
            ]:
                v = getattr(self.world, k, False)
                flags_status.append(f"\033[92m{name}:ON\033[0m" if v else f"\033[91m{name}:OFF\033[0m")
                visible_flags.append(f"{name}:ON" if v else f"{name}:OFF")
            
            # Predictor and AI Disable are mapped differently in loop.py
            v_pred = getattr(self.world, 'flag_use_predictor', getattr(self, 'use_predictor', False))
            flags_status.append(f"\033[92mPRED:ON\033[0m" if v_pred else f"\033[91mPRED:OFF\033[0m")
            visible_flags.append(f"PRED:ON" if v_pred else f"PRED:OFF")
            
            v_dai = getattr(self.world, 'flag_disable_ai', getattr(self.world, 'disable_ai', False))
            flags_status.append(f"\033[92mD_AI:ON\033[0m" if v_dai else f"\033[91mD_AI:OFF\033[0m")
            visible_flags.append(f"D_AI:ON" if v_dai else f"D_AI:OFF")
            
            current_fps = 1 / self.world.execTime if self.world.execTime > 0 else 0
            if getattr(self, 'smoothed_fps', 0.0) == 0.0:
                self.smoothed_fps = current_fps
            else:
                self.smoothed_fps = 0.95 * self.smoothed_fps + 0.05 * current_fps

            # sim_status = " | SIMULADO: ON" if hasattr(self, 'rsim') and local_rsim is not None else ""

            import shutil
            cols = shutil.get_terminal_size().columns
            base_bar = f"Tempo: {time.time()-tempo_zero:7.2f}s | FPS: {self.smoothed_fps:6.2f} | UI: "
            
            flags_str = ""
            visible_len = len(base_bar)
            for i, flag in enumerate(flags_status):
                v_len = len(visible_flags[i]) + 1 # +1 para o espaço
                if visible_len + v_len > cols - 2:
                    break
                flags_str += flag + " "
                visible_len += v_len

            sys.stdout.write(f"\033[1G\033[2K{base_bar}{flags_str}")
            sys.stdout.flush()
            # if time.time()-tempo_zero > 1:
            #     self.running = False

        logging.info("System stopped")

    def run(self):
        self.run_loop()
