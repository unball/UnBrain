import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    import torch
except Exception:
    torch = None

def wrap_pi(a: float) -> float:
    """Wrap angle to [-pi, pi)."""
    return (a + math.pi) % (2 * math.pi) - math.pi

def pose_to_sincos(pose: np.ndarray) -> np.ndarray:
    x, y, th = pose
    return np.array([x, y, math.sin(th), math.cos(th)], dtype=np.float32)

def sincos_to_pose(vec: np.ndarray) -> np.ndarray:
    x, y, s, c = vec
    th = math.atan2(s, c)
    return np.array([x, y, th], dtype=np.float32)

@dataclass
class Frame:
    t: float
    x: float
    y: float
    th: float

@dataclass
class BallFrame:
    t: float
    x: float
    y: float
    vx: float
    vy: float

@dataclass
class Cmd:
    t: float
    v: float
    w: float

class CommandLogger:
    """Mantém histórico de comandos por robô (PC-side)."""
    def __init__(self, maxlen: int = 2000):
        self.maxlen = maxlen
        self.cmds: Dict[int, List[Cmd]] = {}

    def push(self, robot_id: int, v: float, w: float, t: float):
        lst = self.cmds.setdefault(robot_id, [])
        lst.append(Cmd(t=t, v=v, w=w))
        if len(lst) > self.maxlen:
            del lst[: len(lst) - self.maxlen]

    def get_since(self, robot_id: int, t0: float) -> List[Cmd]:
        lst = self.cmds.get(robot_id, [])
        # retorno simples; para performance, use ponteiros/índices
        return [c for c in lst if c.t >= t0]

class FrameLogger:
    """Mantém frames mais recentes por robô e da bola."""
    def __init__(self, maxlen: int = 200):
        self.maxlen = maxlen
        self.frames: Dict[int, List[Frame]] = {}
        self.ball_frames: List[BallFrame] = []

    def push(self, robot_id: int, x: float, y: float, th: float, t: float):
        lst = self.frames.setdefault(robot_id, [])
        lst.append(Frame(t=t, x=x, y=y, th=th))
        if len(lst) > self.maxlen:
            del lst[: len(lst) - self.maxlen]

    def push_ball(self, x: float, y: float, vx: float, vy: float, t: float):
        self.ball_frames.append(BallFrame(t=t, x=x, y=y, vx=vx, vy=vy))
        if len(self.ball_frames) > self.maxlen:
            del self.ball_frames[: len(self.ball_frames) - self.maxlen]

    def latest(self, robot_id: int) -> Optional[Frame]:
        lst = self.frames.get(robot_id, [])
        return lst[-1] if lst else None
        
    def latest_ball(self) -> Optional[BallFrame]:
        return self.ball_frames[-1] if self.ball_frames else None

class KinematicPropagator:
    """
    Propagação cinemática diferencial com comandos (v,w) com Filtro de Inércia (Low-Pass).
    Resolve o Phase Shift ("stop and go") e melhora a integração angular com odometria em arco.
    """
    def __init__(self, tau_act: float = 0.0, inertia_tau: float = 0.15, max_accel_v: float = 3.0, max_accel_w: float = 20.0, slip_factor: float = 0.05):
        self.tau_act = tau_act  # atraso de atuação PC->robô (estimado)
        self.inertia_tau = inertia_tau # constante de tempo do motor 
        self.max_accel_v = max_accel_v
        self.max_accel_w = max_accel_w
        self.slip_factor = slip_factor

    def propagate(self, pose0: np.ndarray, t0: float, t1: float, cmds: List[Cmd]) -> np.ndarray:
        if t1 <= t0:
            return pose0.copy()

        x, y, th = float(pose0[0]), float(pose0[1]), float(pose0[2])

        # Aplica atraso de atuação: comandos efetivos começam em t + tau_act
        shifted = [Cmd(t=c.t + self.tau_act, v=c.v, w=c.w) for c in cmds]

        if not shifted:
            return np.array([x, y, th], dtype=np.float32)

        shifted.sort(key=lambda c: c.t)

        # Como a integração é "stateless" por frame, assumimos que no início da janela
        # a velocidade inercial era 0 e deixamos ela "rampar" durante o histórico.
        v_inercial = 0.0
        w_inercial = 0.0
        
        idx = 0
        while idx + 1 < len(shifted) and shifted[idx + 1].t <= t0:
            idx += 1
            
        v_cmd = shifted[idx].v
        w_cmd = shifted[idx].w
        t = t0

        for j in range(idx + 1, len(shifted)):
            tj = shifted[j].t
            if tj <= t0:
                continue
            if tj >= t1:
                break
            dt = tj - t
            x, y, th, v_inercial, w_inercial = self._step_inertia(x, y, th, v_inercial, w_inercial, v_cmd, w_cmd, dt)
            t = tj
            v_cmd = shifted[j].v
            w_cmd = shifted[j].w

        # integra até t1
        dt = t1 - t
        x, y, th, _, _ = self._step_inertia(x, y, th, v_inercial, w_inercial, v_cmd, w_cmd, dt)
        
        # Garante que o angulo retorne no range [-pi, pi] usando atan2
        th = math.atan2(math.sin(th), math.cos(th))
        return np.array([x, y, th], dtype=np.float32)

    def _step_inertia(self, x: float, y: float, th: float, v_in: float, w_in: float, 
                      v_cmd: float, w_cmd: float, dt: float) -> Tuple[float, float, float, float, float]:
        # 1. Filtro Low-Pass para Inércia (Aceleração limitada)
        alpha = 1.0 - math.exp(-dt / self.inertia_tau) if self.inertia_tau > 0 else 1.0
        v_new_raw = v_in + alpha * (v_cmd - v_in)
        w_new_raw = w_in + alpha * (w_cmd - w_in)
        
        # 1.a Limitação Rígida de Aceleração
        if dt > 0:
            v_accel = (v_new_raw - v_in) / dt
            if abs(v_accel) > self.max_accel_v:
                v_new_raw = v_in + math.copysign(self.max_accel_v, v_accel) * dt
                
            w_accel = (w_new_raw - w_in) / dt
            if abs(w_accel) > self.max_accel_w:
                w_new_raw = w_in + math.copysign(self.max_accel_w, w_accel) * dt

        v_new = v_new_raw
        w_new = w_new_raw

        # 1.b Simulação de Slip Lateral (perda de tração frontal em curvas agressivas)
        if self.slip_factor > 0:
            v_eff = v_new * (1.0 - self.slip_factor * min(1.0, abs(w_new) / 10.0))
        else:
            v_eff = v_new
        
        # 2. Integração exata em arco (Exact Arc Odometry)
        if abs(w_new) < 1e-3:
            # Reta (w quase zero)
            x += v_eff * math.cos(th) * dt
            y += v_eff * math.sin(th) * dt
            th += w_new * dt
        else:
            # Arco de Círculo
            R = v_eff / w_new
            th_new = th + w_new * dt
            x += R * (math.sin(th_new) - math.sin(th))
            y -= R * (math.cos(th_new) - math.cos(th))
            th = th_new
            
        return x, y, th, v_new, w_new

class StatePredictor:
    """
    Estimador online:
    - usa último frame da visão como estado base
    - propaga com histórico de comandos até 'now'
    - aplica rede residual opcional (corrige erro da propagação)
    """
    def __init__(
        self,
        cmd_logger: CommandLogger,
        frame_logger: FrameLogger,
        tau_act: float = 0.02,
        use_residual: bool = False,
        model_path: Optional[str] = None,
        device: str = "cpu",
        history_sec: float = 0.25,
    ):
        self.cmd_logger = cmd_logger
        self.frame_logger = frame_logger
        self.propagator = KinematicPropagator(tau_act=tau_act)
        self.use_residual = use_residual
        self.history_sec = history_sec

        self.device = device
        self.model = None
        if use_residual:
            if torch is None:
                raise RuntimeError("PyTorch não disponível, mas use_residual=True.")
            from .models import ResidualMLP
            self.model = ResidualMLP()
            if model_path is not None:
                try:
                    state = torch.load(model_path, map_location=device, weights_only=True)
                    self.model.load_state_dict(state)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar pesos de {model_path}: {e}")
                    print("⚠️ Desativando rede residual (fallback para cinemática).")
                    self.use_residual = False
            self.model.to(device).eval()

    def estimate_now(self, robot_id: int, t_now: float, lookahead: float = 0.0) -> Optional[np.ndarray]:
        fr = self.frame_logger.latest(robot_id)
        if fr is None:
            return None

        pose0 = np.array([fr.x, fr.y, fr.th], dtype=np.float32)
        cmds = self.cmd_logger.get_since(robot_id, fr.t - self.history_sec)
        
        t_target = t_now + lookahead
        pose_pred = self.propagator.propagate(pose0, fr.t, t_target, cmds)

        if not self.use_residual:
            return pose_pred

        # features simples para residual ego-cêntrico:
        dt_total = max(0.0, t_target - fr.t)
        
        v_cmds = [c.v for c in cmds]
        w_cmds = [c.w for c in cmds]
        
        v_mean = float(np.mean(v_cmds)) if v_cmds else 0.0
        w_mean = float(np.mean(w_cmds)) if w_cmds else 0.0
        v_std = float(np.std(v_cmds)) if v_cmds and len(v_cmds) > 1 else 0.0
        w_std = float(np.std(w_cmds)) if w_cmds and len(w_cmds) > 1 else 0.0

        feat = np.array([dt_total, v_mean, w_mean, v_std, w_std], dtype=np.float32)

        with torch.no_grad():
            x = torch.from_numpy(feat).to(self.device).unsqueeze(0)
            delta_local = self.model(x).squeeze(0).cpu().numpy()

        # delta_local representa correção em (dx_local, dy_local, dth)
        dx_local, dy_local, dth = delta_local
        
        c_th = math.cos(pose_pred[2])
        s_th = math.sin(pose_pred[2])
        
        # Rotação para o referencial global
        dx_global = dx_local * c_th - dy_local * s_th
        dy_global = dx_local * s_th + dy_local * c_th
        
        # Soma o residual
        pose_pred[0] += dx_global
        pose_pred[1] += dy_global
        pose_pred[2] = wrap_pi(pose_pred[2] + dth)

        return pose_pred
