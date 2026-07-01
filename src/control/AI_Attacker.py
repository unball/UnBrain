from control import Control
import sys
import os
import re
import json
import time
import threading
import numpy as np

try:
    from gymnasium.spaces import Box
except ImportError:
    from gym.spaces import Box

sys.path.append("..")


def detect_train_n_enemies(directory):
    """Descobre com quantos inimigos o modelo foi treinado, para que a observação só
    exponha os slots de inimigo que ele está acostumado a ver (modelo 1v1 nunca recebe
    inimigos na obs; 1v3 recebe os 3). A informação não está nos pesos (obs é sempre
    40-dim) nem no checkpoint, então usa:
      1. model_config.json -> {"train_n_enemies": N}  (explícito, robusto)
      2. fallback: maior N nos padrões "1vN" do nome da pasta (ex.: "1v2_&_1v1" -> 2)
    Retorna None se não der para inferir (chamador trata como "sem masking")."""
    # 1. Metadado explícito
    cfg_path = os.path.join(directory, "model_config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            if "train_n_enemies" in cfg:
                return int(cfg["train_n_enemies"])
        except Exception as e:
            print(f"[AI] Falha ao ler model_config.json: {e}", flush=True)

    # 2. Fallback: nome da pasta "1vN"
    base = os.path.basename(os.path.normpath(directory))
    matches = re.findall(r'\d+\s*v\s*(\d+)', base)
    if matches:
        return max(int(m) for m in matches)

    return None
# directory="/home/maranhas/UnBall/Attacker-AI-Training/PPO/ppo_models/selfplay_1v2_&_1v1_curriculum_learning"
directory="/home/maranhas/UnBall/Attacker-AI-Training/PPO/ppo_models/1v1_new_move_wall"
# directory="src/strategy/entity/new_hyper"


class DummyEnv:
    """
    A minimal environment substitute containing only the spaces needed to 
    initialize the PPO model in the isolated worker process, avoiding Pickling issues.
    """
    def __init__(self, action_shape, observation_shape):
        self.action_space = Box(low=-1, high=1, shape=action_shape, dtype=np.float32)
        self.observation_space = Box(low=-1.25, high=1.25, shape=observation_shape, dtype=np.float32)


class AI_Control(Control):
    _shared_models = {}
    _model_lock    = threading.Lock()

    def __init__(self, world, env, observation):
        Control.__init__(self, world)
        self.env = env
        self.observation = observation
        self.time = 0
        self.v_wheel0 = 0
        self.v_wheel1 = 0

        # Informa ao Env com quantos inimigos o modelo foi treinado, para que a
        # observação só exponha os slots de inimigo que a rede está acostumada a ver.
        train_n_enemies = detect_train_n_enemies(directory)
        self.env.train_n_enemies = train_n_enemies
        # print(f"[AI] Modelo '{os.path.basename(directory)}' | train_n_enemies={train_n_enemies}", flush=True)

        # Zero-Order Hold: a política foi treinada a 40 Hz (25 ms por ação). A
        # cadência de inferência tem que casar com o tempo em que a FÍSICA do robô
        # avança — e isso depende do modo:
        #   - rsim/simulado: o loop pode rodar sem cadência (heatmap = ~14x real),
        #     então o relógio de parede fica DESACOPLADO do tempo simulado. Aqui
        #     contamos STEPS do simulador (invariante à velocidade do loop).
        #   - firasim/travesim/fisico: o mundo avança em tempo real, então o
        #     relógio de parede É o tempo físico → usamos time.monotonic.
        self._accelerated     = self.world.mode in ("rsim", "simulado")
        self._timestep_ms     = getattr(self.world, 'rsim_dt_s', 0.016) * 1000
        _TARGET_PERIOD_MS     = 25    # período de inferência do treino (40 Hz)
        self._target_period_ms = _TARGET_PERIOD_MS
        # Modo acelerado: integrador de fase em vez de módulo inteiro.
        # round(25/16)=2 → 31.25 Hz; acumulação fracionária → 40 Hz médio correto.
        self._infer_every_n = max(1, round(_TARGET_PERIOD_MS / self._timestep_ms))  # mantido como fallback
        self._infer_accum   = 0.0   # acumula tempo simulado em ms
        self._step_count = 0
        self._infer_period = _TARGET_PERIOD_MS / 1000.0  # 0.025 s = 40 Hz (período de treinamento)
        self._last_infer_t = 0.0

        # Instantiate PPO exactly once globally to avoid FPS drops on role toggle.
        # Lock garante que dois threads não passem pelo check simultaneamente
        # (TOCTOU), o que causaria monkey-patches de torch.load aninhados incorretamente.
        with AI_Control._model_lock:
            if 'ppo_model' not in AI_Control._shared_models:
                import torch
                from ML_algorithms.PPO import PPO
                from control.AI_Attacker import DummyEnv

                torch.set_num_threads(1)
                dummy_env = DummyEnv(env.action_space.shape, env.observation_space.shape)
                model = PPO(env=dummy_env)

                model.device = torch.device('cpu')
                model.actor.to('cpu')
                if hasattr(model, 'critic'):
                    model.critic.to('cpu')

                from ML_algorithms.PPO import FeedForwardNN
                if not hasattr(FeedForwardNN, '_original_forward'):
                    FeedForwardNN._original_forward = FeedForwardNN.forward
                    def cpu_forward(self, obs, device='cpu'):
                        return self._original_forward(obs, device=device)
                    FeedForwardNN.forward = cpu_forward

                original_torch_load = torch.load
                def cpu_torch_load(*args, **kwargs):
                    kwargs['map_location'] = 'cpu'
                    return original_torch_load(*args, **kwargs)

                torch.load = cpu_torch_load
                try:
                    model.load_model(directory)
                finally:
                    torch.load = original_torch_load

                if hasattr(model, 'actor'):
                    model.actor.eval()

                AI_Control._shared_models['ppo_model'] = model

        self.model = AI_Control._shared_models['ppo_model']

    def output(self, robot):
        robot.direction = 1

        import torch

        # Zero-Order Hold dependente do modo (ver __init__).
        if self._accelerated:
            # rsim/simulado: integrador de fase — acumula tempo simulado e dispara
            # quando cruza o período-alvo. Distribui o erro de arredondamento
            # uniformemente (jitter ≤ 1 timestep) em vez do erro sistemático de
            # round(25/16)=2 → 31.25 Hz.
            self._infer_accum += self._timestep_ms
            if self._infer_accum < self._target_period_ms:
                return self.v_wheel0, self.v_wheel1
            self._infer_accum -= self._target_period_ms  # mantém o resíduo para o próximo ciclo
        else:
            # firasim/travesim/fisico: cadência por relógio de parede (40 Hz),
            # porque aí o relógio real é o próprio tempo físico do mundo.
            now = time.monotonic()
            if (now - self._last_infer_t) < self._infer_period:
                return self.v_wheel0, self.v_wheel1
            self._last_infer_t = now

        self.observation = self.env._get_observation()

        # Inferência determinística: usa a MÉDIA da política (sem amostrar o ruído
        # de exploração do treino) e aplica tanh, exatamente como o ambiente recebia
        # durante o treino (action = tanh(mean)). Isso elimina o tremor e corrige a
        # escala das rodas.
        obs_tensor = torch.tensor(self.observation, dtype=torch.float32, device=self.model.device)
        with torch.no_grad():
            mean = self.model.actor(obs_tensor)
            action = torch.tanh(mean)

        action = action.detach().cpu().numpy().flatten()

        # if not hasattr(self, '_dbg_infer_n'):
        #     self._dbg_infer_n = 0
        # self._dbg_infer_n += 1
        # if self._dbg_infer_n <= 3 or self._dbg_infer_n % 50 == 0:
        #     import sys as _sys
        #     _sys.__stdout__.write(
        #         f"[AI_DBG #{self._dbg_infer_n}] obs[:11]={[round(float(x),3) for x in self.observation[:11]]} "
        #         f"action={[round(float(a),3) for a in action]}\n"
        #     )
        #     _sys.__stdout__.flush()

        self.observation = self.env.step(action)
        self.v_wheel0, self.v_wheel1 = self.env._actions_to_v_wheels(action)

        return self.v_wheel0, self.v_wheel1

    def close(self):
        pass
