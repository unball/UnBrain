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
    """Mantém frames mais recentes por robô."""
    def __init__(self, maxlen: int = 200):
        self.maxlen = maxlen
        self.frames: Dict[int, List[Frame]] = {}

    def push(self, robot_id: int, x: float, y: float, th: float, t: float):
        lst = self.frames.setdefault(robot_id, [])
        lst.append(Frame(t=t, x=x, y=y, th=th))
        if len(lst) > self.maxlen:
            del lst[: len(lst) - self.maxlen]

    def latest(self, robot_id: int) -> Optional[Frame]:
        lst = self.frames.get(robot_id, [])
        return lst[-1] if lst else None

class KinematicPropagator:
    """
    Propagação cinemática diferencial com comandos (v,w) em ZOH.
    Observação: 'v' e 'w' aqui são no referencial do mundo (modelo unicycle).
    """
    def __init__(self, tau_act: float = 0.0):
        self.tau_act = tau_act  # atraso de atuação PC->robô (estimado)

    def propagate(self, pose0: np.ndarray, t0: float, t1: float, cmds: List[Cmd]) -> np.ndarray:
        if t1 <= t0:
            return pose0.copy()

        x, y, th = float(pose0[0]), float(pose0[1]), float(pose0[2])

        # aplica atraso de atuação: comandos efetivos começam em t + tau_act
        # Implementação: desloca os timestamps dos comandos "para frente"
        shifted = [Cmd(t=c.t + self.tau_act, v=c.v, w=c.w) for c in cmds]

        # se não houver comandos, assume v=w=0
        if not shifted:
            return np.array([x, y, th], dtype=np.float32)

        # ordena por tempo
        shifted.sort(key=lambda c: c.t)

        # encontra comando válido em t0: último comando com t <= t0
        # se não existir, usa primeiro comando
        idx = 0
        while idx + 1 < len(shifted) and shifted[idx + 1].t <= t0:
            idx += 1
        v = shifted[idx].v
        w = shifted[idx].w
        t = t0

        # itera nos instantes de mudança de comando
        for j in range(idx + 1, len(shifted)):
            tj = shifted[j].t
            if tj <= t0:
                continue
            if tj >= t1:
                break
            dt = tj - t
            x, y, th = self._step(x, y, th, v, w, dt)
            t = tj
            v = shifted[j].v
            w = shifted[j].w

        # integra até t1
        dt = t1 - t
        x, y, th = self._step(x, y, th, v, w, dt)
        th = wrap_pi(th)
        return np.array([x, y, th], dtype=np.float32)

    @staticmethod
    def _step(x: float, y: float, th: float, v: float, w: float, dt: float) -> Tuple[float, float, float]:
        # integração explícita (Euler). Para mais estabilidade, pode usar RK2/RK4.
        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += w * dt
        return x, y, th

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
                state = torch.load(model_path, map_location=device)
                self.model.load_state_dict(state)
            self.model.to(device).eval()

    def estimate_now(self, robot_id: int, t_now: float) -> Optional[np.ndarray]:
        fr = self.frame_logger.latest(robot_id)
        if fr is None:
            return None

        pose0 = np.array([fr.x, fr.y, fr.th], dtype=np.float32)
        cmds = self.cmd_logger.get_since(robot_id, fr.t - self.history_sec)
        pose_pred = self.propagator.propagate(pose0, fr.t, t_now, cmds)

        if not self.use_residual:
            return pose_pred

        # features simples para residual:
        # - pose0 (sin/cos)
        # - pose_pred (sin/cos)
        # - dt_total
        dt_total = max(0.0, t_now - fr.t)
        feat = np.concatenate([pose_to_sincos(pose0), pose_to_sincos(pose_pred), np.array([dt_total], np.float32)])

        with torch.no_grad():
            x = torch.from_numpy(feat).to(self.device).unsqueeze(0)
            delta = self.model(x).squeeze(0).cpu().numpy()

        # delta representa correção em (x,y,sin,cos)
        pred_sc = pose_to_sincos(pose_pred)
        corr = pred_sc + delta
        # renormaliza sin/cos
        s, c = float(corr[2]), float(corr[3])
        r = math.hypot(s, c)
        if r > 1e-6:
            corr[2] = s / r
            corr[3] = c / r
        return sincos_to_pose(corr)
