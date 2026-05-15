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

def build_pairs(frames: List[FrameRow]) -> Dict[int, List[Tuple[FrameRow, FrameRow]]]:
    pairs: Dict[int, List[Tuple[FrameRow, FrameRow]]] = {}
    by: Dict[int, List[FrameRow]] = {}
    for r in frames:
        by.setdefault(r.robot_id, []).append(r)
    for rid, lst in by.items():
        pairs[rid] = [(lst[i], lst[i+1]) for i in range(len(lst)-1)]
    return pairs

def kinematic_predict(x: float, y: float, th: float, v: float, w: float, dt: float) -> Tuple[float,float,float]:
    x2 = x + v * math.cos(th) * dt
    y2 = y + v * math.sin(th) * dt
    th2 = wrap_pi(th + w * dt)
    return x2, y2, th2

def make_dataset(frames_jsonl: str, cmds_jsonl: str, tau_act: float = 0.02) -> Tuple[np.ndarray, np.ndarray]:
    """
    Dataset residual básico:
      features: [pose0_sincos, pose_pred_sincos, dt] (9)
      target:   [pose_true_sincos - pose_pred_sincos] (4)  (residual em sin/cos)
    Simplificação: usa comando médio no intervalo (ou último comando), sem repropagação piecewise.
    Para maior fidelidade, gere pose_pred com piecewise ZOH (mesmo código do predictor).
    """
    frames = load_frames(frames_jsonl)
    cmds = load_cmds(cmds_jsonl)

    # index cmds por robô para consulta rápida
    cmds_by: Dict[int, List[CmdRow]] = {}
    for c in cmds:
        cmds_by.setdefault(c.robot_id, []).append(c)

    pairs_by = build_pairs(frames)

    X, Y = [], []
    for rid, pairs in pairs_by.items():
        clst = cmds_by.get(rid, [])
        if len(clst) == 0:
            continue

        ci = 0
        for f0, f1 in pairs:
            dt = f1.t - f0.t
            if dt <= 0 or dt > 0.5:
                continue

            # encontra último comando antes de (f0.t + tau_act) e mantém como aproximação
            t_eff = f0.t + tau_act
            while ci + 1 < len(clst) and clst[ci + 1].t <= t_eff:
                ci += 1
            v = clst[ci].v
            w = clst[ci].w

            x_pred, y_pred, th_pred = kinematic_predict(f0.x, f0.y, f0.th, v, w, dt)

            feat = np.concatenate([
                pose_to_sincos(f0.x, f0.y, f0.th),
                pose_to_sincos(x_pred, y_pred, th_pred),
                np.array([dt], np.float32)
            ])
            true_sc = pose_to_sincos(f1.x, f1.y, f1.th)
            pred_sc = pose_to_sincos(x_pred, y_pred, th_pred)
            # residual em sin/cos
            tgt = true_sc - pred_sc

            X.append(feat)
            Y.append(tgt)

    if not X:
        raise RuntimeError("Dataset vazio: verifique logs e timestamps.")
    return np.stack(X).astype(np.float32), np.stack(Y).astype(np.float32)
