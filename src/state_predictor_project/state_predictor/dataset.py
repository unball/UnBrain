import json
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

def wrap_pi(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi

def pose_to_sincos(x: float, y: float, th: float) -> np.ndarray:
    return np.array([x, y, math.sin(th), math.cos(th)], dtype=np.float32)

@dataclass
class FrameRow:
    robot_id: int
    t: float
    x: float
    y: float
    th: float

@dataclass
class CmdRow:
    robot_id: int
    t: float
    v: float
    w: float

def load_frames(frames_jsonl: str) -> List[FrameRow]:
    rows = []
    with open(frames_jsonl, "r") as f:
        for line in f:
            o = json.loads(line)
            rows.append(FrameRow(robot_id=int(o["robot_id"]), t=float(o["t"]), x=float(o["x"]), y=float(o["y"]), th=float(o["th"])))
    rows.sort(key=lambda r: (r.robot_id, r.t))
    return rows

def load_cmds(cmds_jsonl: str) -> List[CmdRow]:
    rows = []
    with open(cmds_jsonl, "r") as f:
        for line in f:
            o = json.loads(line)
            rows.append(CmdRow(robot_id=int(o["robot_id"]), t=float(o["t"]), v=float(o["v"]), w=float(o["w"])))
    rows.sort(key=lambda r: (r.robot_id, r.t))
    return rows

def build_pairs(frames: List[FrameRow], max_steps: int = 10) -> Dict[int, List[Tuple[FrameRow, FrameRow]]]:
    pairs: Dict[int, List[Tuple[FrameRow, FrameRow]]] = {}
    by: Dict[int, List[FrameRow]] = {}
    for r in frames:
        by.setdefault(r.robot_id, []).append(r)
    for rid, lst in by.items():
        pairs[rid] = []
        for i in range(len(lst)):
            for k in range(1, max_steps + 1):
                if i + k < len(lst):
                    pairs[rid].append((lst[i], lst[i+k]))
    return pairs

from .predictor import KinematicPropagator

def kinematic_predict(x: float, y: float, th: float, v: float, w: float, dt: float) -> Tuple[float,float,float]:
    x2 = x + v * math.cos(th) * dt
    y2 = y + v * math.sin(th) * dt
    th2 = wrap_pi(th + w * dt)
    return x2, y2, th2

def make_dataset(frames_jsonl: str, cmds_jsonl: str, tau_act: float = 0.02) -> Tuple[np.ndarray, np.ndarray]:
    """
    Dataset residual ego-cêntrico:
      features: [dt, v_mean, w_mean, v_std, w_std] (5 dims)
      target:   [dx_local, dy_local, dth_local] (3 dims)
    """
    frames = load_frames(frames_jsonl)
    cmds = load_cmds(cmds_jsonl)

    # index cmds por robô para consulta rápida
    cmds_by: Dict[int, List[CmdRow]] = {}
    for c in cmds:
        cmds_by.setdefault(c.robot_id, []).append(c)

    pairs_by = build_pairs(frames)
    propagator = KinematicPropagator(tau_act=tau_act)

    X, Y = [], []
    for rid, pairs in pairs_by.items():
        clst = cmds_by.get(rid, [])
        if len(clst) == 0:
            continue

        for f0, f1 in pairs:
            dt = f1.t - f0.t
            if dt <= 0 or dt > 0.5:
                continue

            # Encontra os comandos no intervalo de tempo
            recent_cmds = [c for c in clst if f0.t - 0.25 <= c.t <= f1.t]
            
            # Propaga usando o mesmo KinematicPropagator usado no predictor.py!
            pose0 = np.array([f0.x, f0.y, f0.th], dtype=np.float32)
            pose_pred = propagator.propagate(pose0, f0.t, f1.t, recent_cmds)
            x_pred, y_pred, th_pred = pose_pred

            # Calcula features baseadas no histórico de comandos
            v_cmds = [c.v for c in recent_cmds]
            w_cmds = [c.w for c in recent_cmds]
            
            v_mean = float(np.mean(v_cmds)) if v_cmds else 0.0
            w_mean = float(np.mean(w_cmds)) if w_cmds else 0.0
            v_std = float(np.std(v_cmds)) if v_cmds and len(v_cmds) > 1 else 0.0
            w_std = float(np.std(w_cmds)) if w_cmds and len(w_cmds) > 1 else 0.0

            feat = np.array([dt, v_mean, w_mean, v_std, w_std], dtype=np.float32)
            
            # Erro em coordenadas globais
            dx_global = f1.x - x_pred
            dy_global = f1.y - y_pred
            dth = wrap_pi(f1.th - th_pred)
            
            # Rotação para o referencial local do preditor
            c_th = math.cos(th_pred)
            s_th = math.sin(th_pred)
            
            dx_local = dx_global * c_th + dy_global * s_th
            dy_local = -dx_global * s_th + dy_global * c_th
            
            tgt = np.array([dx_local, dy_local, dth], dtype=np.float32)

            X.append(feat)
            Y.append(tgt)

    if not X:
        raise RuntimeError("Dataset vazio: verifique logs e timestamps.")
    return np.stack(X).astype(np.float32), np.stack(Y).astype(np.float32)
