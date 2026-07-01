import sys
import os
import time
import subprocess
import json
import threading
import traceback
import atexit # <--- NOVO IMPORT

# --- VACINA ANTI-ZUMBI ---
def protocolo_de_limpeza_worker():
    """Garante que o FiraSim e processos órfãos morrem quando este Worker parar."""
    try:
        # Mata simuladores silenciosamente sem exibir erros no terminal
        os.system("pkill -9 -f firasim > /dev/null 2>&1")
        # Se usar o simulador em C++ do VSS, descomente a linha abaixo:
        # os.system("pkill -9 -f vss_simulator > /dev/null 2>&1")
    except:
        pass

atexit.register(protocolo_de_limpeza_worker)
# -------------------------

# LIMIT OS THREADS AT THE VERY BEGINNING TO AVOID CRASHES
os.environ['OMP_NUM_THREADS'] = '1'

os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

try:
    import cv2
    cv2.setNumThreads(0)
except ImportError:
    pass

def get_venv_python():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_training/env/bin/python'))

class AITrainingWorker:
    def __init__(self):
        self.process = None
        self.updates = []
        self.lock = threading.Lock()

    def start(self, config):
        if self.process is not None and self.process.poll() is None:
            return False

        python_bin = get_venv_python()
        if not os.path.exists(python_bin):
            self.updates.append({'status': 'error', 'error_msg': f"Virtual environment python not found at {python_bin}"})
            return False

        script_path = os.path.abspath(__file__)
        config_json = json.dumps(config)
        
        self.process = subprocess.Popen(
            [python_bin, script_path, config_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        def stdout_reader():
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    try:
                        data = json.loads(line.strip())
                        with self.lock:
                            self.updates.append(data)
                    except:
                        print("Worker Output:", line.strip())
        
        def stderr_reader():
            for line in iter(self.process.stderr.readline, ''):
                if line:
                    print("Worker Error:", line.strip())
                    
        threading.Thread(target=stdout_reader, daemon=True).start()
        threading.Thread(target=stderr_reader, daemon=True).start()
        return True

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.stdin.write(json.dumps({'action': 'stop'}) + '\n')
                self.process.stdin.flush()
            except:
                pass
            # Não daremos 'wait' nem 'terminate' aqui!
            # Se fizermos isso na Thread da interface (GTK), o programa congela.
            # E se dermos um timeout muito curto, ele mata o Worker no meio do salvamento.
            # Mandamos o sinal e a interface ficará aguardando o Worker mandar o status 'stopped' de volta!

    def get_updates(self):
        with self.lock:
            ret = list(self.updates)
            self.updates.clear()
            return ret

    def set_render(self, enabled):
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.stdin.write(json.dumps({'action': 'set_render', 'enabled': enabled}) + '\n')
                self.process.stdin.flush()
            except:
                pass

# --- WORKER SUBPROCESS LOGIC ---
class StdoutQueue:
    def put(self, item):
        print(json.dumps(item), flush=True)

    def put_nowait(self, item):
        self.put(item)
        
    def empty(self):
        import select
        i, _, _ = select.select([sys.stdin], [], [], 0.0)
        return not bool(i)
        
    def get_nowait(self):
        import select
        i, _, _ = select.select([sys.stdin], [], [], 0.0)
        if i:
            line = sys.stdin.readline()
            try:
                return json.loads(line)
            except:
                pass
        return None

class TrainingController:
    def __init__(self, render_enabled=False):
        self.should_stop = False
        self.should_reduce_envs = False
        self.render_enabled = render_enabled
        self.stop_lock = threading.Lock()

    def request_stop(self):
        with self.stop_lock:
            self.should_stop = True

    def check_stop(self):
        with self.stop_lock:
            return self.should_stop

    def request_reduce_envs(self):
        with self.stop_lock:
            self.should_reduce_envs = True

    def check_reduce_envs(self):
        with self.stop_lock:
            return self.should_reduce_envs

    def clear_reduce_envs(self):
        # Limpa o pedido de reduzir ambientes (já estamos reagindo a ele no restart).
        # NUNCA limpa should_stop: um Stop pendente tem que sobreviver ao restart.
        with self.stop_lock:
            self.should_reduce_envs = False

def stdin_listener(controller, queue):
    """Background thread that listens for stop signals"""
    import select
    print("[DEBUG] stdin_listener started", flush=True)
    while True:
        try:
            i, _, _ = select.select([sys.stdin], [], [], 0.5)
            if i:
                line = sys.stdin.readline()
                if not line:
                    break
                print(f"[DEBUG] stdin received: {line}", flush=True)
                try:
                    msg = json.loads(line)
                    if isinstance(msg, dict):
                        if msg.get('action') == 'stop':
                            print("[DEBUG] Stop action detected by listener", flush=True)
                            controller.request_stop()
                            queue.put({'status': 'stopping', 'step': 0, 'msg': '[DEBUG] Stop signal received by listener'})
                            
                            # Interrompe a thread principal imediatamente para não ter que esperar o rollout terminar
                            # import _thread
                            # _thread.interrupt_main()
                            
                        elif msg.get('action') == 'set_render':
                            controller.render_enabled = msg.get('enabled', False)
                except Exception as e:
                    print(f"[DEBUG] Error parsing stdin: {e}", flush=True)
        except Exception as e:
            print(f"[DEBUG] Error in stdin_listener: {e}", flush=True)

def resource_monitor(controller, queue):
    import time
    try:
        import psutil
    except ImportError:
        print("[DEBUG] psutil not installed, resource monitor disabled.", flush=True)
        return
        
    print("[DEBUG] resource_monitor started", flush=True)
    consecutive_high_cpu = 0
    while not controller.check_stop():
        try:
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            if cpu > 95.0:
                consecutive_high_cpu += 1
            else:
                consecutive_high_cpu = 0
                
            if mem.percent > 92.0 or consecutive_high_cpu >= 5:
                print(f"[DEBUG] OVERLOAD DETECTED! RAM: {mem.percent}%, CPU: {cpu}%", flush=True)
                controller.request_reduce_envs()
                queue.put({'status': 'info', 'msg': f'⚠️ Sobrecarga detectada (RAM: {mem.percent}%, CPU: {cpu}%). Reduzindo ambientes...'})
                break  # Exit thread since we will restart anyway
            
            time.sleep(2)
        except Exception as e:
            print(f"[DEBUG] Error in resource_monitor: {e}", flush=True)
            time.sleep(5)

def training_process(queue, config, controller=None):
    try:
        # PATH INJECTION
        ai_training_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_training'))
        if ai_training_dir not in sys.path:
            sys.path.insert(0, ai_training_dir)

        attacker_ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Attacker-AI-Training'))
        ppo_dir = os.path.join(attacker_ai_dir, 'PPO')
        if ppo_dir not in sys.path:
            sys.path.insert(0, ppo_dir)

        rsoccer_dir = os.path.join(ai_training_dir, 'rSoccer')
        if os.path.exists(rsoccer_dir) and rsoccer_dir not in sys.path:
            sys.path.insert(0, rsoccer_dir)

        # pyrefly: ignore [missing-import]
        import torch
        import numpy as np
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA não está disponível! O treino exige GPU para rodar.")

        # pyrefly: ignore [missing-import]
        import gymnasium as gym
        sys.modules['gym'] = gym
        # pyrefly: ignore [missing-import]
        import rsoccer_gym
        # pyrefly: ignore [missing-import]
        from PPO import PPO
        # pyrefly: ignore [missing-import]
        from opponent_pool import OpponentPool
        unbrain_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if sys.path[0] == os.path.dirname(__file__):
            sys.path.pop(0)
        sys.path.insert(0, unbrain_src)

        os.environ['UNBRAIN_HEADLESS'] = '1'
        os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
        
        # EXTREMELY IMPORTANT: Limit CPU threads. With 16 envs, default PyTorch will spawn 16 * num_cores threads,
        # instantly causing an OS soft-lock and freezing the PC.
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        
        torch.set_num_threads(1)

        # pyrefly: ignore [missing-import]
        from tools.vision_noise_gym_wrapper import VisionNoiseGymWrapper
        # pyrefly: ignore [missing-import]
        from tools.entities_gym_wrapper import EntitiesGymWrapper

        class RenderGymWrapper(gym.Wrapper):
            def __init__(self, env, controller):
                super().__init__(env)
                self.last_render_time = 0
                self.controller = controller
            
            def step(self, action, *args, **kwargs):
                try:
                    obs, reward, terminated, truncated, info = self.env.step(action, *args, **kwargs)
                    if self.controller.render_enabled:
                        t = time.time()
                        if t - self.last_render_time > (1.0 / 150.0):
                            self.last_render_time = t
                            frame = self.env.unwrapped.frame
                            
                            blue_robots = []
                            for r_id, r in frame.robots_blue.items():
                                blue_robots.append({'id': r_id, 'x': r.x, 'y': r.y, 'theta': r.theta, 'vx': r.v_x, 'vy': r.v_y, 'vtheta': r.v_theta})
                                
                            yellow_robots = []
                            for r_id, r in frame.robots_yellow.items():
                                yellow_robots.append({'id': r_id, 'x': r.x, 'y': r.y, 'theta': r.theta, 'vx': r.v_x, 'vy': r.v_y, 'vtheta': r.v_theta})
                                
                            state_dict = {
                                'status': 'render_state',
                                'ball': {'x': frame.ball.x, 'y': frame.ball.y, 'vx': frame.ball.v_x, 'vy': frame.ball.v_y},
                                'robots_blue': blue_robots,
                                'robots_yellow': yellow_robots
                            }
                            print(json.dumps(state_dict), flush=True)
                except Exception as e:
                    obs, reward, terminated, truncated, info = self.env.step(action, *args, **kwargs)
                return obs, reward, terminated, truncated, info

        queue.put({'status': 'initializing', 'step': 0})
        

        train_with_allies = config.get('train_with_allies', False)
        n_blue = 3 if train_with_allies else 1

        self_play_enabled = config.get('self_play_enabled', True)
        self_play_1v2_enabled = config.get('self_play_1v2_enabled', False)
        self_play_interval = config.get('self_play_interval', 5)
        
        if self_play_1v2_enabled:
            n_yellow = 2
            self_play_enabled = True
        elif self_play_enabled:
            n_yellow = 1
        else:
            n_yellow = 0

        #w_ball_grad, w_move, w_energy, w_lost_b, w_behind_b, w_posse, w_shot, w_posse_diff, w_goal
        weights = [0.8, 0.17, 2e-4, 0.05, 0.15, 0.0, 0.4, 0.15, 1] if self_play_enabled else [0.8, 0.17, 2e-4, 0.05, 0.15, 0.0, 0.0, 0.0, 1]

        print(weights)

        num_envs = config.get('num_envs', 1)
        
        # PRE-SPAWN SAFEGUARD: Evita crash instantâneo limitando num_envs se não houver RAM/CPU suficiente
        try:
            import psutil
            
            # Checagem de CPU: Se o PC já está gargalando (ex: outro treino rodando), recusar
            cpu_usage = psutil.cpu_percent(interval=1.0)
            if cpu_usage > 90.0:
                print(f"[SAFEGUARD] CPU já está em {cpu_usage}%. Um novo treino com vários envs vai travar o PC.", flush=True)
                queue.put({'status': 'info', 'msg': f'⚠️ Segurança Ativa: CPU já está em {cpu_usage}%. Limitando para 1 ambiente para evitar congelamento.'})
                num_envs = 1
                config['num_envs'] = num_envs
            else:
                mem = psutil.virtual_memory()
                available_ram_mb = mem.available / (1024 * 1024)
                
                # Reserva 2GB (2000MB) EXCLUSIVOS para o sistema operacional não travar
                system_buffer_mb = 2000
                safe_ram_mb = max(0, available_ram_mb - system_buffer_mb)
                
                # Assumindo ~50MB de RAM extra por ambiente PPO/Torch/Gym (Graças ao uso de Fork)
                max_envs_allowed = max(1, int(safe_ram_mb // 50))
                
                if num_envs > max_envs_allowed:
                    print(f"[SAFEGUARD] Reduzindo num_envs de {num_envs} para {max_envs_allowed}. Motivo: Reservando 2GB para o OS (Total Livre Atual: {available_ram_mb:.0f}MB).", flush=True)
                    queue.put({'status': 'info', 'msg': f'⚠️ Segurança Ativa: Ambientes reduzidos de {num_envs} para {max_envs_allowed} para não congelar o PC (RAM livre: {available_ram_mb:.0f}MB)'})
                    num_envs = max_envs_allowed
                    config['num_envs'] = num_envs
        except Exception as e:
            print(f"[SAFEGUARD] Erro ao checar RAM/CPU: {e}", flush=True)
            
        render_hlc = config.get('render_hlc', False)
        
        # O usuário instruiu a desligar a visão se for ligada as envs
        if num_envs > 1:
            render_hlc = False

        def _make_env_fn():
            def _init():
                import sys, os
                # PATH INJECTION FOR SPAWNED PROCESSES
                ai_training_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_training'))
                if ai_training_dir not in sys.path: sys.path.insert(0, ai_training_dir)
                
                attacker_ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Attacker-AI-Training'))
                ppo_dir = os.path.join(attacker_ai_dir, 'PPO')
                if ppo_dir not in sys.path: sys.path.insert(0, ppo_dir)
                
                rsoccer_dir = os.path.join(ai_training_dir, 'rSoccer')
                if os.path.exists(rsoccer_dir) and rsoccer_dir not in sys.path: sys.path.insert(0, rsoccer_dir)
                
                unbrain_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                if unbrain_src not in sys.path: sys.path.insert(0, unbrain_src)
                
                os.environ['OMP_NUM_THREADS'] = '1'
                os.environ['MKL_NUM_THREADS'] = '1'
                os.environ['OPENBLAS_NUM_THREADS'] = '1'
                os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
                os.environ['NUMEXPR_NUM_THREADS'] = '1'
                
                try:
                    import torch
                    torch.set_num_threads(1)
                except ImportError:
                    pass
                
                import gymnasium as gym
                sys.modules['gym'] = gym
                import gymnasium.spaces
                sys.modules['gym.spaces'] = gymnasium.spaces
                import rsoccer_gym
                from tools.entities_gym_wrapper import EntitiesGymWrapper
                from tools.vision_noise_gym_wrapper import VisionNoiseGymWrapper
                
                e = gym.make('VSS-v0', max_episode_steps=200, render_mode="rgb_array", n_robots_blue=n_blue, n_robots_yellow=n_yellow, timestep=0.025, weights=weights, apply_delay=config.get('apply_delay', False))
                if train_with_allies:
                    e = EntitiesGymWrapper(e)
                if config.get('use_vision_noise', True):
                    e = VisionNoiseGymWrapper(e, config=config.get('vision_noise_config', {}))
                return e
            return _init

        if num_envs > 1:
            print(f"Iniciando {num_envs} ambientes em paralelo com AsyncVectorEnv (Fork)...", flush=True)
            env = gym.vector.AsyncVectorEnv([_make_env_fn() for _ in range(num_envs)], context="fork")
        else:
            env = _make_env_fn()()

        total_timesteps = config.get('timesteps', 100000)
        # Reutiliza o controller persistente (criado em run_training_loop) quando
        # passado: assim um Stop pedido em torno de um restart de reduce_envs NÃO é
        # perdido junto com o controller antigo (bug: o Stop caía num controller
        # órfão e o treino continuava). Ao reusar, limpa só o flag de reduce_envs.
        own_stdin_listener = controller is None
        if controller is None:
            controller = TrainingController(render_enabled=render_hlc)
        else:
            controller.render_enabled = render_hlc
            controller.clear_reduce_envs()

        if num_envs == 1:
            env = RenderGymWrapper(env, controller)

        model_name = config.get('model_name', 'unbrain_live_model')
        model_dir = os.path.join(ppo_dir, 'ppo_models', model_name)
        
        # Cria a pasta antes para poder receber a cópia do CSV
        os.makedirs(model_dir, exist_ok=True)
        try: os.chmod(model_dir, 0o777) # <-- LIBERA A PASTA DO WORKER
        except: pass

        model = PPO(env, directory=model_dir)

        # --- PASSO 1: CARREGA O CHECKPOINT (antes de inicializar o pool) ---
        # Isso garante que model.actor/log_std têm os pesos corretos antes do seed.
        retrain_model = config.get('retrain_model', None)
        retrain_dir = None
        if retrain_model:
            retrain_dir = os.path.join(ppo_dir, 'ppo_models', retrain_model)
            if not os.path.exists(retrain_dir):
                retrain_dir = os.path.join(ppo_dir, retrain_model)
            if not os.path.exists(retrain_dir):
                retrain_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../UnBrain/src/strategy/entity/{retrain_model.split('/')[-1]}"))

            if os.path.exists(retrain_dir):
                # --- LÓGICA DE MIGRAÇÃO DO DATASET ---
                dataset_old = os.path.join(retrain_dir, 'dataset.csv')
                dataset_new = os.path.join(model_dir, 'dataset.csv')
                
                # Só migra se não for o mesmo exato diretório (resume simples) e se existir CSV antigo
                if retrain_dir != model_dir and os.path.exists(dataset_old):
                    import csv
                    last_t = 0
                    print(f"[DEBUG] Mesclando dataset antigo: {dataset_old} -> {dataset_new}", flush=True)
                    with open(dataset_old, 'r') as fin, open(dataset_new, 'w', newline='') as fout:
                        reader = csv.DictReader(fin)
                        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
                        if 'model_version' not in fieldnames:
                            fieldnames.append('model_version')
                        
                        writer = csv.DictWriter(fout, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for row in reader:
                            if 'model_version' not in row or not row['model_version']:
                                row['model_version'] = retrain_model.split('/')[-1]
                            writer.writerow(row)
                            try:
                                last_t = max(last_t, float(row.get('t_so_far', 0)))
                            except: pass
                            
                    try: os.chmod(dataset_new, 0o666) # <-- LIBERA O NOVO DATASET COPIADO
                    except: pass
                    # Envia pra UI o aviso de que o histórico foi puxado
                    queue.put({'status': 'dataset_migrated', 'path': dataset_new})
                    
                elif retrain_dir == model_dir and os.path.exists(dataset_old):
                    queue.put({'status': 'dataset_migrated', 'path': dataset_old})

                # Carrega a rede — model.actor tem os pesos corretos a partir daqui
                model.load_model(retrain_dir)
                
                # Se o checkpoint antigo for muito velho e não tiver t_so_far salvo, puxamos do CSV
                if model.t_so_far == 0 and 'last_t' in locals() and last_t > 0:
                    model.t_so_far = last_t
                    
                queue.put({'status': 'initializing', 'step': model.t_so_far, 'msg': f"Model {retrain_model} loaded."})
            else:
                raise FileNotFoundError(f"Retrain model '{retrain_model}' not found.")

        if self_play_enabled:
            pool_dir = os.path.join(model_dir, 'opponent_pool')
            os.makedirs(pool_dir, exist_ok=True)
            
            # --- LÓGICA DE MIGRAÇÃO DO POOL ---
            if retrain_model and retrain_dir is not None and retrain_dir != model_dir:
                old_pool_dir = os.path.join(retrain_dir, 'opponent_pool')
                if os.path.exists(old_pool_dir):
                    import shutil
                    n_files = len([f for f in os.listdir(old_pool_dir) if f.endswith('.pth')])
                    print(f"[Self-Play] Herdando {n_files} oponente(s) do pool de '{retrain_model}'...", flush=True)
                    shutil.copytree(old_pool_dir, pool_dir, dirs_exist_ok=True)

            
            if hasattr(env, 'single_observation_space'):
                obs_dim = env.single_observation_space.shape[0]
                act_dim = env.single_action_space.shape[0]
            else:
                obs_dim = env.observation_space.shape[0]
                act_dim = env.action_space.shape[0]
                
            pool = OpponentPool(
                pool_dir=pool_dir,
                obs_dim=obs_dim,
                act_dim=act_dim,
                max_pool_size=30,
                play_against_latest_ratio=0.8,
                device=str(model.device),
            )
            if pool.pool_size() == 0:
                pool.save_checkpoint(
                    actor_state_dict=model.actor.state_dict(),
                    log_std=model.log_std,
                    iteration=model.t_so_far,
                )

        # Usa o limite da interface como total absoluto em vez de somar ao t_so_far
        total_timesteps = config.get('timesteps', 100000)
        
        # Start background thread to listen for stop signals. Só inicia aqui se o
        # controller for próprio; com controller persistente, o listener já roda em
        # run_training_loop (um só, para não vazar threads que roubam o Stop).
        if own_stdin_listener:
            listener_thread = threading.Thread(target=stdin_listener, args=(controller, queue), daemon=True)
            listener_thread.start()

        resource_thread = threading.Thread(target=resource_monitor, args=(controller, queue), daemon=True)
        resource_thread.start()
        
        print("[DEBUG] Starting training loop", flush=True)

        def training_with_stop_check(ep_total_timesteps):
            avg_returns = []
            all_timesteps = []
            return_variances = []
            
            iteration = 0  # <-- 1. ADICIONE O CONTADOR AQUI
            
            t_start = model.t_so_far

            # Curriculum: cada degrau acrescenta UM novo eixo de dificuldade.
            # Thresholds em frações do orçamento DESTA SESSÃO (t_start -> total), e
            # não do total absoluto: senão, ao retomar um modelo já avançado (ex.:
            # ~24M steps), t_so_far já supera 0.55*total e o treino pularia direto
            # para o stage 4, sem nunca passar pelos stages 1-3.
            #   (fração_da_sessão, stage_alvo, mensagem)
            CURRICULUM_SCHEDULE = [
                (0.15, 2, 'Curriculum: bola em qualquer posição (bola parada)'),
                (0.30, 3, 'Curriculum: robôs em posição livre (bola parada)'),
                (0.55, 4, 'Curriculum: bola com velocidade aleatória (modo caótico)'),
            ]
            session_budget = max(1.0, ep_total_timesteps - t_start)

            def _curriculum_threshold(frac):
                return t_start + frac * session_budget

            def _apply_curriculum_stage(stage):
                """Aplica o stage no env. Em env vetorizado usa set_attr; em env único
                (cadeia de gym.Wrapper, SEM set_attr) escreve direto no unwrapped.
                Sem isso, num_envs==1 lançava AttributeError que era engolido pelo
                try/except e o curriculum ficava preso no default (stage 4)."""
                try:
                    if hasattr(env, 'set_attr'):
                        env.set_attr('curriculum_stage', stage)
                    else:
                        env.unwrapped.curriculum_stage = stage
                    return True
                except Exception as e:
                    print(f"[CURRICULUM] AVISO: falha ao aplicar stage {stage}: "
                          f"{type(e).__name__}: {e}", flush=True)
                    return False

            def _disable_legacy_curriculum_mode():
                # Desativa a flag antiga para evitar conflito (mesmo tratamento vec/único).
                try:
                    if hasattr(env, 'set_attr'):
                        env.set_attr('curriculum_mode', False)
                    else:
                        env.unwrapped.curriculum_mode = False
                except Exception:
                    pass

            # Deriva o stage inicial a partir do progresso já treinado (resume),
            # usando a MESMA tabela das transições para nunca divergir.
            curriculum_stage = 1
            for frac, stage, _ in CURRICULUM_SCHEDULE:
                if model.t_so_far >= _curriculum_threshold(frac):
                    curriculum_stage = stage

            _disable_legacy_curriculum_mode()
            _apply_curriculum_stage(curriculum_stage)
            print(f"[CURRICULUM] Stage inicial={curriculum_stage} "
                  f"(t_so_far={model.t_so_far}, sessão={t_start}->{ep_total_timesteps}).", flush=True)

            while model.t_so_far < ep_total_timesteps:
                iteration += 1  # <-- 2. INCREMENTE AQUI
                
                # Transições de currículo: ao cruzar um threshold, consolida a base
                # com EWC, recarrega e avança UM stage por iteração.
                for frac, next_stage, msg in CURRICULUM_SCHEDULE:
                    threshold = _curriculum_threshold(frac)
                    if curriculum_stage < next_stage and model.t_so_far >= threshold:
                        try:
                            print(f"[CURRICULUM] {model.t_so_far} steps atingidos! {msg}. "
                                  f"Salvando EWC da base consolidada antes da transição.", flush=True)
                            queue.put({'status': 'info', 'step': model.t_so_far, 'msg': msg})
                            if torch.cuda.is_available():
                                torch.cuda.synchronize()
                            model.save_model(env, ppo_filename="ppo_full_checkpoint.pth", use_ewc=True)
                            model.load_model(model.directory)

                            curriculum_stage = next_stage
                            _apply_curriculum_stage(curriculum_stage)
                            print(f"[CURRICULUM] Transicionado para stage {curriculum_stage}.", flush=True)
                        except Exception as e:
                            print(f"[CURRICULUM] Erro na transição para stage {next_stage}: {e}", flush=True)
                        break

                print(f"[DEBUG] Loop iteration, t_so_far={model.t_so_far}, should_stop={controller.check_stop()}", flush=True)

                # Stop tem PRIORIDADE sobre reduce_envs: se ambos estiverem pendentes,
                # honra a parada do usuário em vez de reiniciar com menos ambientes
                # (o restart descartaria o Stop). Por isso check_stop vem primeiro.
                if controller.check_reduce_envs() and not controller.check_stop():
                    print(f"[DEBUG] Reduce envs signal detected at step {model.t_so_far}", flush=True)
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                    try:
                        model.save_model(env, use_ewc=False)
                    except Exception as e:
                        print(f"[DEBUG] EXCEPTION in save_model: {type(e).__name__}: {e}", flush=True)
                    return all_timesteps, avg_returns, 'reduce_envs'

                if controller.check_stop():
                    queue.put({'status': 'stopping', 'step': model.t_so_far, 'msg': 'Preparando checkpoint (Pausado, sem EWC)...'})
                    print(f"[DEBUG] Stop signal detected at step {model.t_so_far}", flush=True)

                    if torch.cuda.is_available():
                        torch.cuda.synchronize()

                    try:
                        # 3. ATUALIZE A PAUSA MANUAL PARA NÃO USAR EWC
                        model.save_model(env, use_ewc=False)
                        print(f"[DEBUG] save_model completed successfully", flush=True)
                    except Exception as e:
                        print(f"[DEBUG] EXCEPTION in save_model: {type(e).__name__}: {e}", flush=True)
                        import traceback
                        print(traceback.format_exc(), flush=True)

                    # Envia path do dataset.csv de volta para UI poder montar gráfico
                    dataset_path = os.path.join(model.directory, 'dataset.csv')
                    queue.put({
                        'status': 'stopped',
                        'step': model.t_so_far,
                        'model_path': model.directory,
                        'dataset_path': dataset_path if os.path.exists(dataset_path) else None,
                        'msg': f'✓ Checkpoint salvo em {model.t_so_far} steps'
                    })

                    return all_timesteps, avg_returns, model.t_so_far

                if self_play_enabled:
                    opp_actor, opp_log_std = pool.sample_opponent()
                    # Move to CPU safely for multiprocessing.Pipe serialization
                    opp_actor_cpu = opp_actor.to('cpu')
                    opp_log_std_cpu = opp_log_std.cpu() if hasattr(opp_log_std, 'cpu') else opp_log_std
                    
                    if num_envs > 1:
                        env.call('set_opponent', opp_actor_cpu, opp_log_std_cpu, device='cpu')
                    else:
                        env.unwrapped.set_opponent(opp_actor_cpu, opp_log_std_cpu, device=str(model.device))
                        
                    # Restore on main process if needed
                    opp_actor.to(model.device)
                    print(f"[Self-Play] Oponente injetado no ambiente de treino para a coleta do próximo lote de experiências.", flush=True)

                batch_obs, batch_acts, batch_log_probs, batch_rtgs, batch_lens, batch_rews_ep, rew_list_old, A_k = model.rollout()

                V = model.critic(batch_obs).squeeze()

                model.t_so_far += sum(batch_lens) if len(batch_lens) > 0 else batch_obs.size(0)
                avg_return = sum(batch_rews_ep) / len(batch_rews_ep) if len(batch_rews_ep) > 0 else 0.0
                variance = np.var(batch_rews_ep) if len(batch_rews_ep) > 0 else 0.0

                avg_returns.append(avg_return)
                all_timesteps.append(model.t_so_far)
                return_variances.append(variance)

                # Salva dataset a cada batch (com identificador de versão)
                rew_list_old['t_so_far'] = model.t_so_far
                rew_list_old['avg_return'] = avg_return
                rew_list_old['model_version'] = model_name # <--- INJEÇÃO DE VERSÃO
                model.write_dataset(rew=rew_list_old)

                # --- DEBUG PRINTS RESTORED ---
                print(f'\nBatch Lens: {batch_lens}\n', flush=True)
                if weights[8] != 0:
                    print(f'Goal Score: {rew_list_old.get("goal_score", 0)}\n', flush=True)
                    print(f'Ally Goals: {rew_list_old.get("goals_blue", 0)}\n', flush=True)
                    print(f'Opponent Goals: {rew_list_old.get("goals_yellow", 0)}\n', flush=True)
                if weights[0] != 0:
                    print(f'Ball grad: {rew_list_old.get("ball_grad", 0)}\n', flush=True)
                if weights[3] != 0:
                    print(f'Lost Ball: {rew_list_old.get("lost_ball", 0)}\n', flush=True)
                if weights[1] != 0:
                    print(f'Move: {rew_list_old.get("move", 0)}\n', flush=True)
                if weights[2] != 0:
                    print(f'Energy: {rew_list_old.get("energy", 0)}\n', flush=True)
                if weights[4] != 0:
                    print(f'Behind Ball: {rew_list_old.get("behind_ball", 0)}\n', flush=True)
                if weights[5] != 0:
                    print(f'Ball Possession Boost: {rew_list_old.get("possession_boost", 0)}\n', flush=True)
                if weights[6] != 0:
                    print(f'Shot on Goal: {rew_list_old.get("shot_on_goal", 0)}\n', flush=True)
                if weights[7] != 0:
                    print(f'Possession Diff: {rew_list_old.get("possession_diff", 0)}\n', flush=True)
                    
                print(f'Wall Collision: {rew_list_old.get("wall_collision", 0.0):.3f}\n', flush=True)

                print(f'Ball Wall Collision: {rew_list_old.get("ball_wall_penalty", 0.0):.3f}\n', flush=True)

                if queue is not None:
                    try:
                        queue.put_nowait({
                            'step': model.t_so_far,
                            'reward': avg_return,
                            'status': 'training',
                            'version': model_name # <--- INJEÇÃO PRA UI
                        })
                    except Exception:
                        pass

                A_k = (A_k - A_k.mean()) / (A_k.std() + 1e-10)

                step = batch_obs.size(0)
                inds = np.arange(step)
                minibatch_size = step // model.num_minibatches
                for _ in range(model.n_updates_per_iteration):
                    frac = (model.t_so_far - t_start) / ep_total_timesteps
                    new_lr = model.lr * (1.0 - frac)
                    new_lr = max(new_lr, 0.0)
                    model.actor_optim.param_groups[0]["lr"] = new_lr
                    model.critic_optim.param_groups[0]["lr"] = new_lr

                    np.random.shuffle(inds)
                    broke_early = False
                    for start in range(0, step, minibatch_size):
                        end = start + minibatch_size
                        idx = inds[start:end]
                        minibatch_obs = batch_obs[idx]
                        minibatch_acts = batch_acts[idx]
                        minibatch_log_probs = batch_log_probs[idx]
                        minibatch_advantage = A_k[idx]
                        minibatch_rtgs = batch_rtgs[idx]

                        V, curr_log_probs, entropy = model.evaluate(minibatch_obs, minibatch_acts)
                        logratios = curr_log_probs - minibatch_log_probs

                        ratios = torch.exp(logratios)
                        approx_kl = ((ratios - 1) - logratios).mean()

                        surr1 = ratios * minibatch_advantage
                        surr2 = torch.clamp(ratios, 1 - model.clip, 1 + model.clip) * minibatch_advantage

                        actor_loss = (-torch.min(surr1, surr2)).mean() - model.ent_coef * entropy.mean()
                        ewc_loss = torch.tensor(0.0, device=model.actor.device if hasattr(model.actor, 'device') else 'cuda' if torch.cuda.is_available() else 'cpu')
                        if model.ewc_fisher is not None and model.ewc_means is not None:
                            ewc_loss = 0
                            for name, param in model.actor.named_parameters():
                                ewc_loss += (model.ewc_fisher[name] * (param - model.ewc_means[name]) ** 2).sum()
                            actor_loss += model.ewc_lambda * ewc_loss

                        critic_loss = torch.nn.MSELoss()(V, minibatch_rtgs)

                        model.actor_optim.zero_grad()
                        actor_loss.backward()
                        torch.nn.utils.clip_grad_norm_(model.actor.parameters(), model.max_grad_norm)
                        model.actor_optim.step()

                        model.critic_optim.zero_grad()
                        critic_loss.backward()
                        torch.nn.utils.clip_grad_norm_(model.critic.parameters(), model.max_grad_norm)
                        model.critic_optim.step()

                        if approx_kl > model.target_kl:
                            broke_early = True
                            break

                    if broke_early:
                        break

                if not hasattr(model, 'tempo'):
                    model.tempo = time.time()
                print(f"Timesteps: {model.t_so_far}, Average Return: {avg_return}, Time passed: {time.time() - model.tempo}", flush=True)

                # <-- 4. ADICIONE O BLOCO DE BACKUP NO FINAL DO WHILE -->
                if iteration % 10 == 0:
                    print(f"[BACKUP] Salvando checkpoint de segurança na iteração {iteration} ({model.t_so_far} steps)...", flush=True)
                    model.save_model(env, ppo_filename="ppo_backup.pth", use_ewc=False)

                if self_play_enabled and iteration % self_play_interval == 0:
                    pool.save_checkpoint(
                        actor_state_dict=model.actor.state_dict(),
                        log_std=model.log_std,
                        iteration=int(model.t_so_far),
                    )

            return all_timesteps, avg_returns, model.t_so_far

        try:
            timesteps_1, avg_returns_1, t_so_far = training_with_stop_check(total_timesteps)
        except KeyboardInterrupt:
            print("\n[DEBUG] Treinamento interrompido via Stop (KeyboardInterrupt)!", flush=True)
            t_so_far = model.t_so_far
            
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                
            try:
                model.save_model(env, use_ewc=False)
                print(f"[DEBUG] Emergency save_model completed successfully", flush=True)
            except Exception as e:
                print(f"[DEBUG] EXCEPTION in emergency save_model: {type(e).__name__}: {e}", flush=True)
                
            dataset_path = os.path.join(model.directory, 'dataset.csv')
            queue.put({
                'status': 'stopped',
                'step': model.t_so_far,
                'model_path': model.directory,
                'dataset_path': dataset_path if os.path.exists(dataset_path) else None,
                'msg': f'✓ Checkpoint salvo de emergência em {model.t_so_far} steps'
            })
            
            try:
                env.close()
            except:
                pass
                
            return 'stopped'

        if t_so_far == 'reduce_envs':
            try:
                env.close()
            except:
                pass
            return 'reduce_envs'

        if not controller.check_stop():
            model.save_model(env)
            queue.put({'status': 'finished', 'step': total_timesteps, 'model_path': model.directory})
            
        try:
            env.close()
        except:
            pass

        return 'done'

    except Exception as e:
        queue.put({'status': 'error', 'error_msg': str(e) + "\n" + traceback.format_exc()})
        return 'error'

def run_training_loop(queue, config_data):
    # Controller e stdin_listener PERSISTENTES: sobrevivem aos restarts de
    # reduce_envs. Antes, cada training_process criava o seu, então um Stop pedido
    # em torno de um restart caía num controller órfão e o treino continuava.
    controller = TrainingController()
    listener_thread = threading.Thread(target=stdin_listener, args=(controller, queue), daemon=True)
    listener_thread.start()

    while True:
        status = training_process(queue, config_data, controller=controller)
        # Só reinicia por sobrecarga se o usuário NÃO pediu Stop nesse meio-tempo.
        if status == 'reduce_envs' and not controller.check_stop():
            current_envs = config_data.get('num_envs', 1)
            if current_envs <= 2:
                # If we are at 2 or 1, we can't reduce further. Stop gracefully.
                queue.put({'status': 'error', 'error_msg': 'Sistema sobrecarregado mesmo com poucos ambientes. Treino abortado por segurança.'})
                break

            # Reduce envs by 2
            config_data['num_envs'] = max(1, current_envs - 2)

            # To resume, we MUST set retrain_model to the model we just checkpointed!
            # The model is saved in config_data['model_name']
            config_data['retrain_model'] = config_data.get('model_name', 'unbrain_live_model')

            queue.put({'status': 'info', 'msg': f'🔄 Reiniciando com {config_data["num_envs"]} ambientes...'})
            time.sleep(2)  # Give OS a moment to clear RAM
        else:
            break

if __name__ == '__main__':
    if len(sys.argv) > 1:
        config_data = json.loads(sys.argv[1])
        run_training_loop(StdoutQueue(), config_data)
