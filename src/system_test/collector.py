"""
Coleta/validacao de testes (heatmap, leaderboard, validacao justa episode-based).

Extraido de loop.py para manter o runtime enxuto. CollectorMixin e herdado por Loop,
entao todos os metodos continuam acessando self.world/self.rsim/self.busyLoop()/self.loop()
exatamente como antes. Os workers de multiprocessing ficam como funcoes de modulo
(pickaveis) e importam Loop de forma lazy para evitar import circular.
"""
import os
import csv
import math
import time
import json
import random
import logging
import multiprocessing
import threading
import sys

import numpy as np
import torch
import matplotlib.pyplot as plt

from UVF_screen import SystemTester
from strategy import AI_Attacker, Attacker, Defender, GoalKeeper
from tools.teleport_math import apply_safe_jitter, calculate_teleport_positions, calculate_ball_teleport

class RefereeState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "PLAYING"
        self.ball_xs = []               # janela deslizante de X
        self.ball_ys = []               # janela deslizante de Y
        self.impasse_time = 0.0
        self.gk_hold_time = 0.0
        self.last_t = -1.0              # mantido por compatibilidade
        self.last_stuck_t = -1.0        # mantido por compatibilidade
        self._t_last_tick = None        # relógio interno da FSM (time.monotonic)
        self._t_last_stuck_sample = -1.0  # monotonic do último sample de stuck-ball

    def tick(self) -> float:
        """Retorna dt em segundos desde o último tick, usando time.monotonic().
        Independente de world.execTime, que pode conter Unix timestamp ou zero."""
        now = time.monotonic()
        if self._t_last_tick is None:
            self._t_last_tick = now
            return 0.016  # dt inicial seguro (1 frame @ 62.5 Hz)
        dt = now - self._t_last_tick
        self._t_last_tick = now
        return dt


class StepMetrics:
    """Acumula as métricas-por-passo de futebol, compartilhadas entre o coletor
    time-based (run_single_collect) e o episode-based (run_episodes_collect)."""
    NEAR = 0.12          # limiar de "perto da bola" (posse/toque), em metros
    SPIN_W_DEG = 300.0   # |w| acima disso + vel. baixa = giro parado
    SPRINT_V = 0.6       # vel. linear acima disso = sprint
    SHOT_V = 0.5         # vel. da bola rumo ao gol acima disso = chute

    def __init__(self, world):
        self.side = world.field.side
        self.goal_x = world.field.maxX
        self.goal_half = world.field.goalAreaHeight / 2  # meia-boca do gol
        self.atk_third_x = self.goal_x / 3.0             # início do terço de ataque

        self.ball_dist_total = 0.0
        self.robot_dist_total = 0.0
        self.ball_progress_total = 0.0
        self.prev_ball = None
        self.prev_robot = None
        self.just_reset = True
        self.near_ball_steps = 0
        self.touch_count = 0
        self.touches_box = 0
        self.was_near = False
        self.spin_idle_steps = 0
        self.sprint_steps = 0
        self.speed_sum = 0.0
        self.field_tilt_steps = 0
        self.shots = 0
        self.shots_on_target = 0
        self.was_shooting = False
        self.out_lateral_count = 0
        self.reset_count = 0

    def mark_reset(self, lateral=False):
        """Sinaliza um reset/início de cenário: pula o delta de distância do próximo
        passo (teleporte) e conta o reset (e saída lateral, se for o caso)."""
        self.reset_count += 1
        if lateral:
            self.out_lateral_count += 1
        self.just_reset = True

    def step(self, atacante, ball_x, ball_y, ball_vx, ball_vy):
        """Acumula as métricas deste passo a partir do estado atual do mundo."""
        if atacante is None:
            self.just_reset = False
            return
        rx, ry = atacante.x, atacante.y

        # Distâncias percorridas (ignora o salto causado pelo reset)
        if not self.just_reset:
            if self.prev_ball is not None:
                self.ball_dist_total += math.hypot(ball_x - self.prev_ball[0], ball_y - self.prev_ball[1])
                prog = self.side * (ball_x - self.prev_ball[0])  # só avanço rumo ao gol
                if prog > 0:
                    self.ball_progress_total += prog
            if self.prev_robot is not None:
                self.robot_dist_total += math.hypot(rx - self.prev_robot[0], ry - self.prev_robot[1])

        # Posse / toques (robô perto da bola)
        is_near = math.hypot(ball_x - rx, ball_y - ry) < self.NEAR
        if is_near:
            self.near_ball_steps += 1
            if not self.was_near:
                self.touch_count += 1
                if self.side * ball_x > self.atk_third_x:  # toque na área de ataque
                    self.touches_box += 1
        self.was_near = is_near

        # Movimento do robô
        v = atacante.velmod
        self.speed_sum += v
        if v < 0.05 and abs(np.rad2deg(atacante.w)) > self.SPIN_W_DEG:
            self.spin_idle_steps += 1
        if v > self.SPRINT_V:
            self.sprint_steps += 1

        # Field tilt: bola no terço de ataque
        if self.side * ball_x > self.atk_third_x:
            self.field_tilt_steps += 1

        # Detecção de chute (bola rumo ao gol cruzando o limiar)
        if self.side * ball_vx > self.SHOT_V:
            if not self.was_shooting:
                self.shots += 1
                dx = self.side * self.goal_x - ball_x
                if abs(ball_vx) > 1e-6:
                    y_at_goal = ball_y + (ball_vy / ball_vx) * dx
                    if abs(y_at_goal) < self.goal_half:
                        self.shots_on_target += 1
            self.was_shooting = True
        else:
            self.was_shooting = False

        self.prev_ball = (ball_x, ball_y)
        self.prev_robot = (rx, ry)
        self.just_reset = False

    def to_dict(self, steps):
        """Campos de métricas ricas para o dict de retorno do coletor."""
        return {
            "steps": steps,
            "ball_dist_total": self.ball_dist_total,
            "robot_dist_total": self.robot_dist_total,
            "ball_progress_total": self.ball_progress_total,
            "near_ball_steps": self.near_ball_steps,
            "touch_count": self.touch_count,
            "touches_box": self.touches_box,
            "spin_idle_steps": self.spin_idle_steps,
            "sprint_steps": self.sprint_steps,
            "speed_sum": self.speed_sum,
            "field_tilt_steps": self.field_tilt_steps,
            "shots": self.shots,
            "shots_on_target": self.shots_on_target,
            "out_lateral_count": self.out_lateral_count,
            "reset_count": self.reset_count,
        }


_ODE_EXCLUSION_RADIUS = 0.04  # 4 cm — garante folga suficiente para o solver ODE

def _ode_safe_positions(positions: list) -> list:
    """Dispersa robôs co-localizados radialmente para prevenir 'LCP internal error' do ODE.
    Atua sobre uma lista de [x, y, th] e retorna cópia com separação mínima garantida."""
    safe = [list(p) for p in positions]
    for i in range(len(safe)):
        for j in range(i + 1, len(safe)):
            dx = safe[j][0] - safe[i][0]
            dy = safe[j][1] - safe[i][1]
            dist = math.hypot(dx, dy)
            if dist < _ODE_EXCLUSION_RADIUS:
                if dist > 1e-9:
                    scale = (_ODE_EXCLUSION_RADIUS - dist) / dist
                    safe[j][0] += dx * scale
                    safe[j][1] += dy * scale
                else:
                    # co-localização exata: empurra diagonalmente para não sobrepor
                    safe[j][0] += _ODE_EXCLUSION_RADIUS * math.cos(j * 1.0)
                    safe[j][1] += _ODE_EXCLUSION_RADIUS * math.sin(j * 1.0)
    return safe


class CollectorMixin:
    def start_episode_test_thread(self, seed, max_steps=1200, n_episodes=1, n_enemies=0, enemy_entity="", is_fixed=True):
        """[UI Coupled] Inicia uma thread daemon para rodar o teste de episódio isolado."""
        self.episode_testing_running = True
        self.episode_thread = threading.Thread(
            target=self._episode_test_worker,
            args=(seed, max_steps, n_episodes, n_enemies, enemy_entity, is_fixed),
            daemon=True
        )
        self.episode_thread.start()

    def _episode_test_worker(self, seed, max_steps=1200, n_episodes=1, n_enemies=0, enemy_entity="", is_fixed=True):
        """[UI Coupled] Worker que executa a simulação episódica."""
        # Propaga n_enemies para _apply_restart e _get_observation (AI)
        self.episode_n_enemies = n_enemies
        self.world.episode_n_enemies = n_enemies
        # Modo 1v1: prepara o world espelhado que controla o inimigo via entidade escolhida.
        self.episode_enemy_entity = enemy_entity
        self.enemy_control_output = None
        self._enemy_cmd_error_logged = False
        self._ensure_enemy_world()
        seeds = [seed + i for i in range(n_episodes)]
        try:
            result = self.run_episodes_collect(seeds, max_episode_steps=max_steps, render=False, is_ui_coupled=True, is_fixed=is_fixed)
            self._save_episode_heatmap(result)
        except OSError:
            # Socket IPC fechou (UI morreu antes do episódio terminar) — encerra silenciosamente.
            pass
        except Exception:
            import traceback
            traceback.print_exc()
        finally:
            # Garante a limpeza da flag mesmo em caso de exceção inesperada.
            self.episode_testing_running = False
            # Limpa o estado do 1v1 para o loop normal não computar comando de inimigo.
            self.episode_enemy_entity = ""
            self.enemy_control_output = None
            self.enemy_world = None

    def _save_episode_heatmap(self, result):
        """Gera e persiste o heatmap em data/heatmap_result.png a partir do resultado de um teste UI."""
        import os
        x_positions = result.get("x_positions", [])
        y_positions = result.get("y_positions", [])
        if not x_positions:
            return
        try:
            tester = SystemTester(self.world)
            fig = tester.gera_heatmap(x_positions, y_positions)
            os.makedirs("data", exist_ok=True)
            fig.savefig("data/heatmap_result.png", dpi=120, bbox_inches="tight")
            sys.__stdout__.write("\r\033[K[UI] heatmap salvo em data/heatmap_result.png\n"); sys.__stdout__.flush()
            
            # --- LEADERBOARD & METRICS NO UI TEST ---
            register_dict = {
                "runningtime": [result.get("runningtime", 0.0)],
                "goalcount aliado": [result.get("goals_aliado", [])],
                "goalcount inimigo": [result.get("goals_inimigo", [])],
                "stuckball": [result.get("stuckball", [])]
            }
            
            # Recriando o `agg` com os agregados de result
            agg_keys = ['out_lateral_count', 'passes_count', 'intercept_count', 'finalization_count', 'time_in_enemy_half', 'time_with_ball', 'total_distance_ally', 'total_distance_ball', 'heatmap_x_mean', 'heatmap_y_mean', 'pos_ball_x_mean', 'pos_ball_y_mean']
            agg = {k: result.get(k, 0.0) for k in agg_keys}
            
            data_dict = tester.gera_datadict(register_dict)
            with open("data/heatmap_stats.json", "w") as f:
                import json
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
                
            sys.__stdout__.write("\r\033[K[AGG] ===== ESTATÍSTICAS AGREGADAS (UI) =====\n"); sys.__stdout__.flush()
            for key, value in data_dict.items():
                sys.__stdout__.write(f"\r\033[K[AGG]  {key}: {value}\n"); sys.__stdout__.flush()
                
            try:
                from control.AI_Attacker import directory as ppo_dir
                import os
                model = os.path.basename(ppo_dir.rstrip('/')) if self.test_type == "heatmap_attacker_ia" else "—"
            except Exception:
                model = "—"
            
            attacker = {"heatmap_attacker_ia": "AI_Attacker(PPO)",
                        "heatmap_attacker": "Attacker(classic)",
                        "heatmap_defender": "Defender",
                        "heatmap_goalkeeper": "GoalKeeper"}.get(self.test_type, str(self.test_type))
                        
            metrics = tester.gera_report_metrics(register_dict, agg)
            identity = {"model": model, "attacker": attacker,
                        "runtime_s": round(result.get("runningtime", 0.0), 1), "n_sims": 1,
                        "mode": "episode_ui", "num_episodes": len(result.get("goals_aliado", [])) + len(result.get("goals_inimigo", [])) or 1,
                        "max_episode_steps": 1200}
                        
            # Divide o leaderboard por cenário
            enemy_name = getattr(self, "episode_enemy_entity", "")
            if getattr(self, "episode_n_enemies", 0) > 0 and enemy_name:
                csv_path = f"data/ai_leaderboard_{enemy_name}.csv"
            else:
                csv_path = "data/ai_leaderboard_normal.csv"
                
            tester.append_leaderboard(csv_path, identity, metrics)
            # ----------------------------------------
            
            try:
                import subprocess
                subprocess.Popen(['xdg-open', 'data/heatmap_result.png'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        except Exception as e:
            sys.__stdout__.write(f"\r\033[K[UI] Falha ao salvar heatmap/leaderboard: {e}\n"); sys.__stdout__.flush()

    def stop_episode_test(self):
        """[UI Coupled] Sinaliza para a thread parar a execução episódica."""
        self.episode_testing_running = False

    def _reset_sim(self):
        """Reposiciona bola e robôs de forma aleatória válida no PRÓPRIO simulador (self.rsim)."""
        ball_pos, pos_robots = self.get_valid_positions(len(self.world.n_robots))
        if getattr(self, 'team_yellow', False):
            self.rsim.reset(ball_pos, [], pos_robots)
        else:
            self.rsim.reset(ball_pos, pos_robots, [])
            
        if getattr(self, 'enemy_world', None) and getattr(self.enemy_world, 'team', None):
            self.enemy_world.team[0].spin = 0
            self.enemy_world.team[0].spinTime = 0

    def _resolve_heatmap_entity(self):
        """Resolve a classe-alvo do heatmap a partir do test_type (uma vez)."""
        if self.test_type == "heatmap_attacker_ia":
            return AI_Attacker
        elif self.test_type == "heatmap_attacker":
            return Attacker
        elif self.test_type == "heatmap_defender":
            return Defender
        elif self.test_type == "heatmap_goalkeeper":
            return GoalKeeper
        return None

    def _resolve_enemy_entity(self):
        """Resolve a classe da entidade que controla o inimigo no modo 1v1."""
        return {
            "goalkeeper":  GoalKeeper,
            "attacker":    Attacker,
            "defender":    Defender,
            "ai_attacker": AI_Attacker,
        }.get(getattr(self, 'episode_enemy_entity', ''), None)

    def _ensure_enemy_world(self):
        """Cria (uma vez) um World ESPELHADO para controlar o inimigo no 1v1.
        side invertido + team_yellow oposto fazem as entidades clássicas (GoalKeeper,
        Attacker, Defender) enxergarem o campo na perspectiva certa, sem modificá-las."""
        entity_class = self._resolve_enemy_entity()
        if entity_class is None:
            self.enemy_world = None
            return
        from world import World
        ally_side = self.world.field.side
        self.enemy_world = World(
            n_robots=[0],
            side=-ally_side,
            team_yellow=not self.world.team_yellow,
            rsim=True,
            simulado=getattr(self.world, 'simulado', False),
            AI_attacker=(entity_class is AI_Attacker),
        )
        self.enemy_world.rsim_dt_s = getattr(self.world, 'rsim_dt_s', 0.016)
        self.enemy_world.team[0].updateEntity(entity_class)
        print(f"[1v1] Inimigo controlado por {entity_class.__name__} (world espelhado side={-ally_side})\n"); sys.__stdout__.flush()

    def _compute_enemy_command(self):
        """Sincroniza o world espelhado a partir do world aliado já atualizado e roda a
        entidade do inimigo, retornando (vl, vr) prontos para o rsim.step(). Guarda em
        self.enemy_control_output. Usa coords RAW (globais); o field.side=-1 inverte."""
        e = getattr(self, 'enemy_world', None)
        if e is None:
            self.enemy_control_output = None
            return None

        ally = self.world.team[self.n_robots[0]]
        enemy_global = self.world.enemies[0]
        if enemy_global is None or ally is None:
            self.enemy_control_output = None
            return None

        try:
            dt = e.rsim_dt_s
            # O inimigo global vira o "time" do world espelhado. _raw_th é o ângulo bruto
            # (radianos, frame global) que raw_update consome — round-trip consistente.
            e.team[0].raw_update(enemy_global.raw_x, enemy_global.raw_y, enemy_global._raw_th)
            e.team[0].calc_velocities(dt)
            # A bola é a mesma (coords globais).
            e.ball.raw_update(self.world.ball.raw_x, self.world.ball.raw_y)
            e.ball.calc_velocities(dt)
            # O aliado global vira o "inimigo" do world espelhado.
            if e.enemies[0] is not None:
                e.enemies[0].raw_update(ally.raw_x, ally.raw_y, ally._raw_th)
                e.enemies[0].calc_velocities(dt)

            robot = e.team[0]
            robot.updateSpin()
            robot.turnOn()
            robot.entity.fieldDecider()
            robot.entity.directionDecider()
            vl, vr = robot.entity.control.actuateSimu(robot)
            self.enemy_control_output = (float(vl), float(vr))
        except Exception:
            # Loga o traceback completo UMA vez para diagnóstico (não floodar o log).
            if not getattr(self, '_enemy_cmd_error_logged', False):
                self._enemy_cmd_error_logged = True
                import traceback
                print("[1v1] ERRO ao computar comando do inimigo (entidade congelará):\n"); sys.__stdout__.flush()
                traceback.print_exc()
            self.enemy_control_output = (0.0, 0.0)
        return self.enemy_control_output

    def run_single_collect(self, duracao=300, render=False):
        """
        Roda UMA simulação completa (self.rsim/self.world) por `duracao` segundos de
        relógio, o mais rápido possível (sem sleep de cadência, para acumular dados
        mais rápido), e devolve os dados coletados.

        Pensado para rodar dentro de um processo isolado (multiprocessing): cada
        processo tem sua própria Loop/World/rsim, então NÃO há estado compartilhado
        nem corrida de threads. A física avança em self.rsim dentro de self.loop().
        """
        t0 = 0
        pid = os.getpid()
        logger = logging.getLogger(f"PID-{pid}")

        entity_class = self._resolve_heatmap_entity()

        x_positions, y_positions = [], []
        goals_aliado, goals_inimigo, stuckball = [], [], []
        last_ball_xs, last_ball_ys = [], []

        # ---- Acumuladores de métricas ricas (relatório/leaderboard) ----
        m = StepMetrics(self.world)

        tempo_zero = time.time()
        tempo_atual_local = 0.0
        cronometro_5s = cronometro_1s = 0.0
        last_reset_time = -1
        steps = 0  # [DEBUG] nº de passos de simulação executados

        logger.info("System is running")
        print(f"[SIM {pid}] iniciado | test_type={self.test_type} | duracao={duracao}s\n"); sys.__stdout__.flush()

        # ---- render setup (apenas n_sims=1, processo principal) ----
        _render_ax = None
        _render_last_t = 0.0
        _RENDER_DT = 1 / 5  # 5 fps
        if render:
            try:
                import matplotlib.pyplot as _plt
                import matplotlib.patches as _mp
                _plt.ion()
                _render_fig, _render_ax = _plt.subplots(figsize=(9, 7))
                _render_ax.set_aspect('equal')
                _plt.tight_layout()
                _plt.show(block=False)
            except Exception as _e:
                print(f"[RENDER] aviso: não foi possível abrir janela gráfica ({_e})\n"); sys.__stdout__.flush()
                _render_ax = None

        original_testing_flag = getattr(self, 'episode_testing_running', False)
        self.episode_testing_running = True
        try:
            while tempo_atual_local < duracao:
                tempo_atual_local = time.time() - tempo_zero
                flag_1s = flag_5s = False
                if tempo_atual_local - cronometro_5s > 5:
                    flag_5s = True
                    cronometro_5s = tempo_atual_local
                if tempo_atual_local - cronometro_1s > 1:
                    flag_1s = True
                    cronometro_1s = tempo_atual_local

                # Avança visão -> mundo (busyLoop) e estratégia -> rsim.step (loop).
                # Mesma ordem do run_loop principal: primeiro percebe, depois age.
                self.busyLoop()
                self.loop()
                steps += 1
                
                # True execution time of the full cycle
                self.world.execTime = time.time() - t0

                ball_x, ball_y = self.world.ball.x, self.world.ball.y

                # ---- Coleta de métricas ricas (por passo) ----
                atacante = self.world.team[self.n_robots[0]]
                m.step(atacante, ball_x, ball_y, self.world.ball.vx, self.world.ball.vy)

                # ---- render visual (apenas single-process) ----
                if _render_ax is not None:
                    _t_now = time.time()
                    if _t_now - _render_last_t >= _RENDER_DT:
                        _render_last_t = _t_now
                        _render_ax.cla()
                        _render_ax.set_facecolor('#1a6b2a')
                        _render_ax.set_xlim(-0.85, 0.85)
                        _render_ax.set_ylim(-0.72, 0.72)
                        _render_ax.set_aspect('equal')
                        # Linhas estáticas do campo (sem patches separados — usa plot para velocidade)
                        _render_ax.plot([-0.75,-0.75,0.75,0.75,-0.75], [-0.65,0.65,0.65,-0.65,-0.65], 'w-', lw=1.5)
                        _render_ax.axvline(0, c='white', lw=1, alpha=0.4)
                        _render_ax.add_patch(_mp.Circle((0, 0), 0.2, fill=False, ec='white', lw=1))
                        # Gols
                        _render_ax.plot([0.75,0.85,0.85,0.75], [-0.2,-0.2,0.2,0.2], color='#ffff00', lw=2)
                        _render_ax.plot([-0.75,-0.85,-0.85,-0.75], [-0.2,-0.2,0.2,0.2], color='#4444ff', lw=2)
                        # Bola
                        _render_ax.add_patch(_mp.Circle((ball_x, ball_y), 0.022, color='orange', zorder=5))
                        # Robôs aliados
                        for _r in self.world.raw_team:
                            if _r is None:
                                continue
                            _ent = type(_r.entity).__name__ if _r.entity is not None else ''
                            _col = '#ff4444' if _ent == 'AI_Attacker' else '#eeee00'
                            _render_ax.add_patch(_mp.Circle((_r.x, _r.y), 0.038, color=_col, ec='black', lw=1.5, zorder=6))
                            # seta de direção via plot (muito mais rápido que annotate)
                            _render_ax.plot(
                                [_r.x, _r.x + 0.07 * np.cos(_r.th)],
                                [_r.y, _r.y + 0.07 * np.sin(_r.th)],
                                'k-', lw=2, zorder=7
                            )
                        _render_ax.set_title(
                            f't={tempo_atual_local:.1f}/{duracao}s  |  pos={len(x_positions)}'
                            f'  |  gols A/I={len(goals_aliado)}/{len(goals_inimigo)}'
                        )
                        _render_fig.canvas.draw_idle()
                        _render_fig.canvas.flush_events()

                # [DEBUG] progresso ~1x/s: quem é o processo, quanto rodou, velocidade e o que coletou
                if flag_1s:
                    fps = steps / tempo_atual_local if tempo_atual_local > 0 else 0.0
                    print(
                        f"[SIM {pid}] t={tempo_atual_local:5.1f}/{duracao}s | passos={steps} "
                        f"(~{fps:5.1f}/s) | pos={len(x_positions)} | gols A/I={len(goals_aliado)}/{len(goals_inimigo)} "
                        f"| stuck={len(stuckball)} | bola=({ball_x:+.2f},{ball_y:+.2f})",
                        flush=True,
                    )
                goal_status = self.world.field.insideGoalNet((ball_x, ball_y))
                # Gol aliado / inimigo (self.world.rsim é True tanto p/ rsim quanto simulado)
                if flag_1s:
                    last_ball_xs.insert(0, ball_x)
                    last_ball_ys.insert(0, ball_y)
                    if len(last_ball_xs) > 5:
                        last_ball_xs.pop()
                        last_ball_ys.pop()
                goal_status = self.world.field.insideGoalNet((ball_x, ball_y))
                # Bola parada -> reset
                if flag_5s and len(last_ball_xs) >= 5 and \
                   np.std(last_ball_xs) < 1e-4 and np.std(last_ball_ys) < 1e-4:
                    moving_ball_time = (tempo_atual_local - last_reset_time - 5) if last_reset_time != -1 \
                        else (tempo_atual_local + 1 - 5)
                    stuckball.append(moving_ball_time)
                    last_ball_xs, last_ball_ys = [], []
                    self._reset_sim()
                    last_reset_time = tempo_atual_local
                    m.mark_reset()
                    goal_status = self.world.field.insideGoalNet((ball_x, ball_y))

                
                elif (self.world.rsim or getattr(self.world, 'simulado', False)) and goal_status == "ally_goal":
                    goals_aliado.append(tempo_atual_local - last_reset_time if last_reset_time != -1
                                        else tempo_atual_local + 1)
                    self._reset_sim()
                    last_reset_time = tempo_atual_local
                    m.mark_reset()
                elif (self.world.rsim or getattr(self.world, 'simulado', False)) and goal_status == "enemy_goal":
                    goals_inimigo.append(tempo_atual_local - last_reset_time if last_reset_time != -1
                                         else tempo_atual_local + 1)
                    self._reset_sim()
                    last_reset_time = tempo_atual_local
                    m.mark_reset()
                elif (self.world.rsim or getattr(self.world, 'simulado', False)) and abs(self.world.ball.y) > self.world.field.maxY:
                    self._reset_sim()
                    last_reset_time = tempo_atual_local
                    m.mark_reset(lateral=True)

                # Coleta de posições para o heatmap
                for robot in self.world.raw_team:
                    if robot is None:
                        continue
                    if (entity_class is None and self.test_type != "heatmap_ball") or \
                       (entity_class is not None and isinstance(robot.entity, entity_class)):
                        x_positions.append(round(robot.x, 3))
                        y_positions.append(round(robot.y, 3))
                    elif self.test_type == "heatmap_ball":
                        x_positions.append(round(ball_x, 3))
                        y_positions.append(round(ball_y, 3))
        finally:
            self.episode_testing_running = original_testing_flag
            if render and getattr(self, '_render_ax', None) is not None:
                try:
                    import matplotlib.pyplot as _plt
                    _plt.close('all')
                except Exception:
                    pass
            logger.info(f"System stopped, position list size: {len(x_positions)}")
            print(f"[SIM {pid}] FIM | passos={steps} | pos={len(x_positions)} "
                  f"| gols A/I={len(goals_aliado)}/{len(goals_inimigo)} | stuck={len(stuckball)}\n"); sys.__stdout__.flush()

        return {
            "x_positions": x_positions,
            "y_positions": y_positions,
            "goals_aliado": goals_aliado,
            "goals_inimigo": goals_inimigo,
            "stuckball": stuckball,
            "runningtime": tempo_atual_local,
            # Métricas ricas (relatório/leaderboard)
            **m.to_dict(steps),
        }

    # ------------------------------------------------------------------ #
    # Validação justa episode-based (espelha ai_training/PPO/test.py)
    # ------------------------------------------------------------------ #
    def _apply_restart(self, foul, kicker_is_ally, quadrant, is_goalie_top, jitter=True):
        is_left_side = not getattr(self, 'team_yellow', False)
        n_robots = len(self.world.n_robots)
        
        enemy_is_kicker = not kicker_is_ally
        
        is_fixed = getattr(self, '_current_is_fixed', True)
        
        if not is_fixed:
            ally_placements = {}
            enemy_placements = {}
            max_x = self.world.field.maxX - 0.1
            max_y = self.world.field.maxY - 0.1
            
            for i in range(n_robots):
                ally_placements[i] = {
                    "x": random.uniform(-max_x, max_x),
                    "y": random.uniform(-max_y, max_y),
                    "th": random.uniform(-np.pi, np.pi)
                }
            for i in range(3):
                enemy_placements[i] = {
                    "x": random.uniform(-max_x, max_x),
                    "y": random.uniform(-max_y, max_y),
                    "th": random.uniform(-np.pi, np.pi)
                }
            ball_pos = [random.uniform(-max_x, max_x), random.uniform(-max_y, max_y)]
        else:
            enemy_placements = calculate_teleport_positions(foul, enemy_is_kicker, not is_left_side, 3, quadrant, is_goalie_top)
            ally_placements = calculate_teleport_positions(foul, kicker_is_ally, is_left_side, n_robots, quadrant, is_goalie_top)
            
            if jitter:
                ally_placements = apply_safe_jitter(ally_placements, self.world.field.maxX, self.world.field.maxY)
                enemy_placements = apply_safe_jitter(enemy_placements, self.world.field.maxX, self.world.field.maxY)

            ball_pos = calculate_ball_teleport(foul, quadrant, is_left_side if kicker_is_ally else not is_left_side,
                                           self.world.field.maxX * 2, self.world.field.maxY * 2)

        is_rsim = self.world.rsim or getattr(self.world, 'simulado', False)
        if is_rsim:
            # Em rsim, rsim.reset() teleporta tudo instantaneamente — não usamos
            # teleport_mode/TeleportEntity, pois dentro do loop de episódio não há
            # fase de espera de posicionamento e os robôs nunca chegariam à formação.
            ally_list = []
            for i in range(n_robots):
                if i in ally_placements:
                    p = ally_placements[i]
                    ally_list.append([p["x"], p["y"], p["th"]])
                else:
                    ally_list.append([-0.3 - i * 0.2, 0.0, 0.0])

            n_enemies = getattr(self, 'episode_n_enemies', 0)
            enemy_list = []
            for i in range(3):
                # Só os primeiros n_enemies entram em campo (1v1 -> só o inimigo 0).
                if i < n_enemies and i in enemy_placements:
                    p = enemy_placements[i]
                    enemy_list.append([p["x"], p["y"], p["th"]])
                else:
                    enemy_list.append([0.0, 2.0 + i * 0.2, 0.0])  # fora do campo

            # Garante separação mínima entre todos os robôs para evitar o crash
            # "ODE Message 3: LCP internal error" causado por co-localização.
            ally_list  = _ode_safe_positions(ally_list)
            enemy_list = _ode_safe_positions(enemy_list)

            # Exceção Blind: os robôs inimigos atuarão como barreiras físicas passivas
            # e a IA aliada não os vê (obs[25:40]=0 no wrap).
            if getattr(self, 'team_yellow', False):
                self.rsim.reset(ball_pos, enemy_list, ally_list)
            else:
                self.rsim.reset(ball_pos, ally_list, enemy_list)
        else:
            # Sem rsim (firasim/travesim): a bola e os inimigos vão por setPos instantâneo;
            # os ALIADOS são conduzidos até a formação via teleport.py (TeleportEntity).
            #
            # Por que teleport_mode (e não setPos nos aliados): com entidades fixas
            # (flag_static_entities/force_entities) a estratégia sobrescreve a entidade de
            # cada robô TODO ciclo, então logo após um setPos os robôs voltam a jogar e
            # "passam por cima" do reposicionamento. O bloco de teleport_mode em
            # strategy.update() roda ANTES do bloco de static_entities e faz `return`,
            # tomando o controle enquanto o reset acontece. As fases de espera em
            # run_episodes_collect (_robots_arrived) aguardam a chegada e então limpam o
            # teleport_mode, devolvendo o controle às entidades fixas.
            n_enemies = getattr(self, 'episode_n_enemies', 0)
            sim_client = getattr(self, 'firasim', getattr(self, 'travesim', None))
            if sim_client:
                sim_client.command.setBallPos(ball_pos[0], ball_pos[1])
                # Inimigos: só os primeiros n_enemies em campo, resto fora (setPos instantâneo).
                for i in range(3):
                    if i < n_enemies and i in enemy_placements:
                        p = enemy_placements[i]
                        sim_client.command.setPos(i, p["x"], p["y"], p["th"], is_enemy=True)
                    else:
                        sim_client.command.setPos(i, 0.0, 2.0 + i * 0.2, 0.0, is_enemy=True)

            # Aliados: conduzidos pela estratégia (teleport_mode) até a formação.
            reset_formation = []
            for i in range(len(self.world.n_robots)):
                if i in ally_placements:
                    p = ally_placements[i]
                    reset_formation.append({'x': p["x"], 'y': p["y"], 'th': p["th"]})
            self.world.teleport_config["_episode_reset"] = reset_formation
            self.world.teleport_mode = "_episode_reset"

    def _build_restart_scenario(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        try:
            torch.manual_seed(seed)
        except Exception:
            pass
        
        is_fixed = getattr(self, '_current_is_fixed', True)

        if is_fixed:
            foul = random.choice(['KICKOFF', 'FREE_BALL', 'PENALTY_KICK', 'GOAL_KICK', 'FREE_KICK'])
        else:
            foul = 'KICKOFF'
            
        kicker_is_ally = random.choice([True, False])
        quadrant = random.choice([1, 2, 3, 4])
        is_goalie_top = random.choice([True, False])
        
        self._apply_restart(foul, kicker_is_ally, quadrant, is_goalie_top)

    def _referee_event(self, ref):
        ball_x, ball_y = self.world.ball.x, self.world.ball.y
        maxX, maxY = self.world.field.maxX, self.world.field.maxY
        GOAL_HALF_W = self.world.field.goalAreaHeight / 2  # 0.20 m

        # Consome flags transient recebidas do interceptor da visão (Gols rápidos que entraram e saíram do gol)
        transient_ally = getattr(self.world, 'transient_goal_aliado', False)
        transient_enemy = getattr(self.world, 'transient_goal_inimigo', False)
        self.world.transient_goal_aliado = False
        self.world.transient_goal_inimigo = False

        goal_status = self.world.field.insideGoalNet((ball_x, ball_y))
        
        # Gol aliado (bola cruzou x = +maxX em direção ao gol inimigo)
        if goal_status == "ally_goal" or transient_ally:
            print(f"[DEBUG REFEREE] Goal Aliado! (x={ball_x:.3f}) -> KICKOFF Inimigo\n"); sys.__stdout__.flush()
            return ('KICKOFF', False, 0, True)

        # Gol inimigo (bola cruzou x = -maxX em direção ao gol aliado)
        if goal_status == "enemy_goal" or transient_enemy:
            print(f"[DEBUG REFEREE] Goal Inimigo! (x={ball_x:.3f}) -> KICKOFF Aliado\n"); sys.__stdout__.flush()
            return ('KICKOFF', True, 0, True)
            
        quadrant = 1
        if ball_x >= 0 and ball_y >= 0: quadrant = 1
        elif ball_x < 0 and ball_y >= 0: quadrant = 2
        elif ball_x < 0 and ball_y < 0: quadrant = 3
        elif ball_x >= 0 and ball_y < 0: quadrant = 4
        
        if abs(ball_y) > maxY:
            print(f"[DEBUG REFEREE] Bola fora (lateral)! (y={ball_y:.2f}) -> FREE_BALL (quad {quadrant})\n"); sys.__stdout__.flush()
            return ('FREE_BALL', True, quadrant, True)
            
        # Relógio próprio da FSM — independente de world.execTime (que pode conter
        # Unix timestamp ou zero dependendo do modo de execução).
        dt = ref.tick()

        in_enemy_area = (ball_x >= maxX - 0.15) and (abs(ball_y) <= 0.35)
        in_ally_area = (ball_x <= -maxX + 0.15) and (abs(ball_y) <= 0.35)

        if in_ally_area:
            from strategy import GoalKeeper
            gk_near = any(
                r is not None
                and isinstance(r.entity, GoalKeeper)
                and math.hypot(r.x - ball_x, r.y - ball_y) < 0.12
                for r in self.world.team
            )
            if gk_near:
                ref.gk_hold_time += dt
                ref.impasse_time = 0.0
            else:
                ref.impasse_time += dt
                ref.gk_hold_time = 0.0

            if ref.gk_hold_time >= 5.0:
                print(f"[DEBUG REFEREE] Goleiro Aliado segurou por 5s! -> PENALTY_KICK Inimigo\n"); sys.__stdout__.flush()
                return ('PENALTY_KICK', False, quadrant, ball_y >= 0)
            elif ref.impasse_time >= 5.0:
                print(f"[DEBUG REFEREE] Impasse na área Aliada por 5s! -> GOAL_KICK Inimigo\n"); sys.__stdout__.flush()
                return ('GOAL_KICK', True, quadrant, ball_y >= 0)

        elif in_enemy_area:
            ref.impasse_time += dt
            ref.gk_hold_time = 0.0  # evita disparo espúrio de PENALTY ao re-entrar na área aliada
            if ref.impasse_time >= 5.0:
                print(f"[DEBUG REFEREE] Impasse na área Inimiga por 5s! -> GOAL_KICK Aliado\n"); sys.__stdout__.flush()
                return ('GOAL_KICK', False, quadrant, ball_y >= 0)
        else:
            ref.impasse_time = 0.0
            ref.gk_hold_time = 0.0

            # Stuck ball: amostra a cada ~1 s de relógio monotônico
            now_mono = time.monotonic()
            if ref._t_last_stuck_sample < 0 or (now_mono - ref._t_last_stuck_sample) >= 1.0:
                ref._t_last_stuck_sample = now_mono
                ref.ball_xs.append(ball_x)
                ref.ball_ys.append(ball_y)
                if len(ref.ball_xs) > 5:
                    ref.ball_xs.pop(0)
                    ref.ball_ys.pop(0)

                if len(ref.ball_xs) == 5 and np.std(ref.ball_xs) < 1e-4 and np.std(ref.ball_ys) < 1e-4:
                    print(f"[DEBUG REFEREE] Bola presa (stuck) por 5s! -> FREE_BALL\n"); sys.__stdout__.flush()
                    return ('FREE_BALL', True, quadrant, True)

        return None

    def _robots_arrived(self, tol=0.1):
        """True quando todos os robôs em modo TeleportEntity chegaram aos alvos."""
        from strategy.entity.teleport import TeleportEntity
        teleporting = [r for r in self.world.team
                       if r is not None and isinstance(r.entity, TeleportEntity)]
        if not teleporting:
            return False  # estratégia ainda não atribuiu as TeleportEntity
        for r in teleporting:
            if np.hypot(r.x - r.entity.target_x, r.y - r.entity.target_y) > tol:
                return False
        return True

    def run_episodes_collect(self, episode_seeds, max_episode_steps, render=False, is_ui_coupled=False, is_fixed=True):
        """Validação justa: roda os episódios de `episode_seeds` (cenários seeded), cada um
        do reset até gol/saída/timeout, acumulando as MESMAS métricas de run_single_collect.
        Single-env. Em backends não-robosim roda em cadência real-time (time.sleep)."""
        pid = os.getpid()
        logger = logging.getLogger(f"PID-{pid}")
        entity_class = self._resolve_heatmap_entity()
        is_rsim = self.world.rsim or getattr(self.world, 'simulado', False)
        is_mainsystem = getattr(self.world, 'mainsystem', False)
        n0 = self.n_robots[0]

        x_positions, y_positions = [], []
        goals_aliado, goals_inimigo, stuckball = [], [], []
        m = StepMetrics(self.world)
        total_steps = 0
        DT = getattr(self.world, 'rsim_dt_s', 0.016)  # passo físico simulado (s)

        print(f"[SIM {pid}] validação justa | {len(episode_seeds)} episódios | "
              f"seeds={episode_seeds[:8]}{'...' if len(episode_seeds) > 8 else ''}\n"); sys.__stdout__.flush()

        def _tick():
            """Um ciclo percebe→age, com cadência real-time fora do robosim."""
            t0 = time.time()
            self.busyLoop()
            self.loop()
            
            # [ENG] Se a UI principal estiver pausada (execute == False),
            # o loop.py não envia os pacotes para o FiraSim. Precisamos garantir 
            # que os robôs andem até a posição durante a fase de teleporte/reset.
            if not is_rsim and not getattr(self, 'execute', False) and getattr(self.world, "firasim", False):
                try:
                    actions = [r.entity.control.actuateSimu(r) if (r and hasattr(r.entity, 'control') and r.entity.control) else (0, 0) for r in self.world.team]
                    self.firasim.command.writeMulti([(v, w) for v, w in actions], robot_ids=[r.id for r in self.world.team if r is not None])
                except Exception:
                    pass

            if not is_rsim:
                rest = self.loopTime - (time.time() - t0)
                if rest > 0:
                    time.sleep(rest)

        original_testing_flag = getattr(self, 'episode_testing_running', False)
        self.episode_testing_running = True
        try:
            for seed in episode_seeds:
                if is_ui_coupled and not original_testing_flag:
                    break
                
                if is_mainsystem and not is_ui_coupled:
                    try:
                        input(f"\n[VALIDAÇÃO] Episódio seed={seed}: posicione a bola e aperte ENTER "
                              f"(os robôs vão se posicionar sozinhos)...")
                    except EOFError:
                        pass

                self._build_restart_scenario(seed)

                # --- Fase de posicionamento inicial ---
                print(f'"posicionando" {self.world.teleport_mode}')
                if not is_rsim:
                    pos_watchdog = 10.0
                    t_start = time.time()
                    while not self._robots_arrived() and (time.time() - t_start) < pos_watchdog:
                        self.world.teleport_mode = "_episode_reset"
                        if is_ui_coupled and not getattr(self, 'episode_testing_running', False):
                            break
                        _tick()
                    else:
 
                        print('fim do posicionamento')
                        self.world.teleport_mode = None

                try:
                    ctrl = self.world.team[n0].entity._control
                    if hasattr(ctrl, '_step_count'):
                        ctrl._step_count = 0
                except Exception:
                    pass

                m.mark_reset()

                # --- Episódio: mini-partida contínua ---
                ep_steps = 0
                referee = RefereeState()
                
                while ep_steps < max_episode_steps:
                    if is_ui_coupled and not getattr(self, 'episode_testing_running', False):
                        break
                        
                    _tick()
                    ep_steps += 1
                    total_steps += 1

                    ball_x, ball_y = self.world.ball.x, self.world.ball.y
                    atacante = self.world.team[n0]
                    m.step(atacante, ball_x, ball_y, self.world.ball.vx, self.world.ball.vy)

                    for robot in self.world.raw_team:
                        if robot is None:
                            continue
                        if (entity_class is None and self.test_type != "heatmap_ball") or \
                           (entity_class is not None and isinstance(robot.entity, entity_class)):
                            x_positions.append(round(robot.x, 3))
                            y_positions.append(round(robot.y, 3))
                        elif self.test_type == "heatmap_ball":
                            x_positions.append(round(ball_x, 3))
                            y_positions.append(round(ball_y, 3))

                    # Referee FSM
                    ev = self._referee_event(referee)
                    if ev is not None:
                        foul, kicker_is_ally, quadrant, is_goalie_top = ev
                        
                        if foul == 'KICKOFF':
                            if kicker_is_ally:
                                goals_inimigo.append(ep_steps * DT)
                            else:
                                goals_aliado.append(ep_steps * DT)
                        elif foul == 'FREE_BALL' and abs(ball_y) > self.world.field.maxY:
                            m.out_lateral_count += 1
                        elif foul == 'FREE_BALL':
                            stuckball.append(ep_steps * DT)
                            
                        self._apply_restart(foul, kicker_is_ally, quadrant, is_goalie_top)
                        
                        if not is_rsim:
                            pos_watchdog = 10.0
                            t_restart = time.time()
                            while not self._robots_arrived() and (time.time() - t_restart) < pos_watchdog:
                                self.world.teleport_mode = "_episode_reset"
                                if is_ui_coupled and not getattr(self, 'episode_testing_running', False):
                                    break
                                _tick()
                        self.world.teleport_mode = None
                        
                        try:
                            ctrl = self.world.team[n0].entity._control
                            if hasattr(ctrl, '_step_count'):
                                ctrl._step_count = 0
                        except Exception:
                            pass
                            
                        m.mark_reset()
                        referee.reset()

                print(f"[SIM {pid}] seed={seed} | steps={ep_steps} | "
                      f"gols A/I={len(goals_aliado)}/{len(goals_inimigo)}\n"); sys.__stdout__.flush()
        finally:
            self.episode_testing_running = original_testing_flag
            logger.info(f"System stopped, position list size: {len(x_positions)}")
            print(f"[SIM {pid}] FIM validação | episódios={len(episode_seeds)} | passos={total_steps} "
                  f"| gols A/I={len(goals_aliado)}/{len(goals_inimigo)}\n"); sys.__stdout__.flush()

        return {
            "x_positions": x_positions,
            "y_positions": y_positions,
            "goals_aliado": goals_aliado,
            "goals_inimigo": goals_inimigo,
            "stuckball": stuckball,
            "runningtime": total_steps * DT,  # tempo SIMULADO (s), comparável entre modelos
            **m.to_dict(total_steps),
        }

    def test(self, n_threads=1, duracao=300, render=False, num_episodes=0, max_episode_steps=1200):
            import json
            # inicializa testador
            tester = SystemTester(self.world)

            if self.draw_uvf:
                # cria thread do loop, importante pois mesmo as threads não interagindo bem com o matplotlib isso permite que o loop rode normalmente.
                self.loop_thread = threading.Thread(target=self.run_loop)
                self.loop_thread.start()

                # O parâmetro render_uvf=True desacelera o render do matplotlib, esteja ciente disso ao habilitar
                # Quanto mais setas no render do uvf, mais lento fica o render. Aumentar a quantidade de setas sem diminuir a loop_freq *não vai adiantar*, o render vai ficar lento.
                tester.run_singletest(loop=self, robot_i=0, render_uvf=False)

                self.loop_thread.join()
                return

            # =====================================================================
            # [UNBALL ENG] COLETA PARALELA VIA MULTIPROCESSING
            # =====================================================================
            # Threads NÃO aceleram aqui: o GIL serializa a estratégia (Python puro) e
            # o robosim (pybind11/C++) segura o GIL durante o step(). Para acumular
            # dados mais rápido cada simulação roda em seu PRÓPRIO processo, com sua
            # própria World/rsim — paralelismo real que escala com os núcleos da CPU.
            # Os resultados são coletados e agregados aqui no processo principal.
            # =====================================================================
            is_rsim = self.world.rsim or getattr(self.world, 'simulado', False)
            fair = num_episodes > 0      # validação justa episode-based (seeds 0..N-1)
            mode = "episode" if fair else "time"

            if fair and is_rsim and n_threads > 1:
                # Validação justa PARALELA (robosim): pré-partição round-robin dos seeds
                # 0..N-1 entre os K workers (worker w → {w, w+K, …}). Garante cenários
                # únicos por env, sem repetição, e conjunto idêntico/reprodutível entre
                # modelos — equivalente spawn-safe ao SeedValueWrapper do test.py.
                os.environ.setdefault("OMP_NUM_THREADS", "1")
                os.environ.setdefault("MKL_NUM_THREADS", "1")
                sys.__stdout__.write(f"\r\033[K[AGG]  validação justa: {num_episodes} episódios seeded em {n_threads} "
                      f"processos | max_steps={max_episode_steps}\n"); sys.__stdout__.flush()
                ctx = multiprocessing.get_context("spawn")
                seed_slices = [list(range(w, num_episodes, n_threads)) for w in range(n_threads)]
                worker_args = [(self._init_kwargs, sl, max_episode_steps) for sl in seed_slices]
                pool = ctx.Pool(processes=n_threads)
                results = pool.map(_run_episode_worker, worker_args)
                pool.close()
                pool.join()
            elif fair:
                # Single-env (FIRASim/TraveSim/mainsystem, ou n_threads==1): roda os N
                # episódios seeded em sequência no processo atual, em cadência real-time
                # quando não-robosim. Backends externos/físico não paralelizam.
                if n_threads > 1 and not is_rsim:
                    print("[AGG] backend não-robosim: paralelismo desativado, rodando n_sims=1.\n"); sys.__stdout__.flush()
                results = [self.run_episodes_collect(list(range(num_episodes)),
                                                     max_episode_steps, render=render)]
            elif n_threads > 1:
                # ---- Time-based PARALELO (legado) ----
                # Limita threads internas ANTES do spawn para os filhos herdarem no
                # import do torch. Sem isso, N processos abrem N*muitas threads de
                # OpenMP/MKL e travam por oversubscription (1 worker roda, 2+ congelam).
                os.environ.setdefault("OMP_NUM_THREADS", "1")
                os.environ.setdefault("MKL_NUM_THREADS", "1")

                # 'spawn' (não 'fork'): o projeto importa torch no topo do módulo e dar
                # fork depois disso trava (deadlock de threads/CUDA). O pré-flight já
                # define spawn como start method global; usamos o mesmo aqui.
                sys.__stdout__.write(f"\r\033[K[AGG]  lançando {n_threads} processos | duracao={duracao}s cada\n"); sys.__stdout__.flush()
                ctx = multiprocessing.get_context("spawn")
                worker_args = [(self._init_kwargs, duracao, seed) for seed in range(n_threads)]
                # close()+join() (em vez de `with ... as pool`) encerra os workers de
                # forma graciosa: o context manager chama terminate() (SIGTERM nos filhos),
                # o que disparava o handler de sinal herdado de main.py antes da agregação.
                pool = ctx.Pool(processes=n_threads)
                results = pool.map(_run_sim_worker, worker_args)
                pool.close()
                pool.join()
            else:
                # Time-based single (legado): roda direto no processo atual
                results = [self.run_single_collect(duracao=duracao, render=render)]

            # ----- Agregação dos resultados de todos os processos -----
            x_positions, y_positions = [], []
            runningtime_register = []
            goal_register_aliado, goal_register_inimigo, stuckball_register = [], [], []
            # Soma dos campos numéricos das métricas ricas
            agg_keys = ["steps", "ball_dist_total", "robot_dist_total", "ball_progress_total",
                        "near_ball_steps", "touch_count", "touches_box", "spin_idle_steps",
                        "sprint_steps", "speed_sum", "field_tilt_steps", "shots",
                        "shots_on_target", "out_lateral_count", "reset_count"]
            agg = {k: 0.0 for k in agg_keys}
            for r in results:
                x_positions.extend(r["x_positions"])
                y_positions.extend(r["y_positions"])
                runningtime_register.append(r["runningtime"])
                goal_register_aliado.append(r["goals_aliado"])
                goal_register_inimigo.append(r["goals_inimigo"])
                stuckball_register.append(r["stuckball"])
                for k in agg_keys:
                    agg[k] += r.get(k, 0)

            sys.__stdout__.write(f"\r\033[K[AGG]  {len(results)} processos concluídos | posições totais={len(x_positions)} "
                  f"| gols A={sum(len(g) for g in goal_register_aliado)} "
                  f"I={sum(len(g) for g in goal_register_inimigo)} "
                  f"| stuck={sum(len(s) for s in stuckball_register)}\n"); sys.__stdout__.flush()

            fig = tester.gera_heatmap(x_positions, y_positions)

            # cria dicionário de registros de dados da simulação
            register_dict = {"runningtime": runningtime_register,
                             "goalcount aliado": goal_register_aliado,
                             "goalcount inimigo": goal_register_inimigo,
                             "stuckball": stuckball_register}

            data_dict = tester.gera_datadict(register_dict)

            # Persiste resultados em disco: o print() do projeto passa por um logger
            # com QueueListener que pode não esvaziar no shutdown, e sob backend headless
            # o plt.show() não abre janela. Salvar garante que nada se perca.
            os.makedirs("data", exist_ok=True)
            try:
                fig.savefig("data/heatmap_result.png", dpi=120, bbox_inches="tight")
            except Exception as e:
                sys.__stdout__.write(f"\r\033[K[AGG]  falha ao salvar heatmap: {e}\n"); sys.__stdout__.flush()
            with open("data/heatmap_stats.json", "w") as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)

            # print mais bonitinho dos dados (flush p/ não perder no shutdown)
            print("[AGG] ===== ESTATÍSTICAS AGREGADAS =====\n"); sys.__stdout__.flush()
            for key, value in data_dict.items():
                sys.__stdout__.write(f"\r\033[K[AGG]  {key}: {value}\n"); sys.__stdout__.flush()
            print("[AGG] salvos: data/heatmap_result.png e data/heatmap_stats.json\n"); sys.__stdout__.flush()

            # ----- Relatório rico + leaderboard acumulativo -----
            try:
                from control.AI_Attacker import directory as ppo_dir
                model = os.path.basename(ppo_dir.rstrip('/')) if self.test_type == "heatmap_attacker_ia" else "—"
            except Exception:
                model = "—"
            attacker = {"heatmap_attacker_ia": "AI_Attacker(PPO)",
                        "heatmap_attacker": "Attacker(classic)",
                        "heatmap_defender": "Defender",
                        "heatmap_goalkeeper": "GoalKeeper"}.get(self.test_type, str(self.test_type))

            metrics = tester.gera_report_metrics(register_dict, agg)
            identity = {"model": model, "attacker": attacker,
                        "runtime_s": round(sum(runningtime_register), 1), "n_sims": len(results),
                        "mode": mode, "num_episodes": num_episodes if fair else 0,
                        "max_episode_steps": max_episode_steps if fair else 0}
            
            # Divide o leaderboard por cenário
            enemy_name = getattr(self, "episode_enemy_entity", "")
            if getattr(self, "episode_n_enemies", 0) > 0 and enemy_name:
                csv_path = f"data/ai_leaderboard_{enemy_name}.csv"
            else:
                csv_path = "data/ai_leaderboard_normal.csv"
                
            tester.append_leaderboard(csv_path, identity, metrics)

            plt.show()


def _run_sim_worker(args):
    """
    Worker de processo (multiprocessing): constrói uma Loop independente a partir
    dos kwargs originais e roda UMA simulação de coleta. Recebe uma tupla
    (init_kwargs, duracao, seed) e devolve o dict de dados de run_single_collect.

    Precisa ficar no nível do módulo para ser picklável pelo multiprocessing.
    """
    init_kwargs, duracao, seed = args

    # Com 'spawn', cada worker importa main.py (como __mp_main__) e herda os handlers
    # de SIGINT/SIGTERM definidos lá no nível do módulo. Quando o Pool é encerrado
    # (terminate()), esse handler dispara nos workers, imprime "[MAIN] Sinal recebido"
    # e chama sys.exit(0) ANTES da agregação no processo-pai rodar. Resetamos os sinais
    # para o comportamento padrão para que o worker morra limpo, sem rodar o handler.
    import signal as _signal
    _signal.signal(_signal.SIGINT, _signal.SIG_IGN)
    _signal.signal(_signal.SIGTERM, _signal.SIG_DFL)

    # Cada worker é um processo dedicado a UMA simulação. Se cada um abrir várias
    # threads de torch/OpenMP/MKL, N processos disputam os mesmos núcleos e podem
    # travar (oversubscription/deadlock sob 'spawn'). Limitamos a 1 thread por worker
    # para que o paralelismo venha dos PROCESSOS, não das threads internas.
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    # Sementes distintas por processo para que as simulações não fiquem idênticas
    random.seed(seed)
    np.random.seed(seed)

    kwargs = dict(init_kwargs)
    kwargs["draw_uvf"] = False  # nada de GUI/UVF dentro dos workers
    from loop import Loop  # lazy: evita import circular com loop.py
    worker_loop = Loop(**kwargs)
    return worker_loop.run_single_collect(duracao=duracao)


def _run_episode_worker(args):
    """
    Worker da validação justa: constrói uma Loop independente e roda a FATIA de seeds
    (episódios) atribuída a este processo. Recebe (init_kwargs, episode_seeds,
    max_episode_steps) e devolve o dict de dados de run_episodes_collect.

    A semeadura é POR-EPISÓDIO (dentro de run_episodes_collect), não por processo,
    garantindo que o seed K gere sempre o mesmo cenário independentemente de qual
    worker o execute (comparação justa e reprodutível entre modelos).
    """
    init_kwargs, episode_seeds, max_episode_steps = args

    # Mesmo reset de sinais do _run_sim_worker: evita o handler herdado de main.py
    # disparar nos workers no shutdown do Pool.
    import signal as _signal
    _signal.signal(_signal.SIGINT, _signal.SIG_IGN)
    _signal.signal(_signal.SIGTERM, _signal.SIG_DFL)

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    kwargs = dict(init_kwargs)
    kwargs["draw_uvf"] = False
    from loop import Loop  # lazy: evita import circular com loop.py
    worker_loop = Loop(**kwargs)
    return worker_loop.run_episodes_collect(episode_seeds, max_episode_steps)
