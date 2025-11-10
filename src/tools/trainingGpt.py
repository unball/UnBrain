import torch
import torch.nn as nn
import torch.optim as optim
import time
import numpy as np
import os
import sys
from typing import Tuple, Optional, Dict, Any

from src.tools import speeds2motors, motors2speeds_from_vl_vr, r, L

def analytic_transform(wL_s: float, wR_s: float, r_t: float=r, L_t: float=L) -> Tuple[float, float]:
    # target wheel linear velocities
    vL_t = wL_s * r_t
    vR_t = wR_s * r_t
    # target body velocities
    v_t = 0.5 * (vL_t + vR_t)
    w_t = (vR_t - vL_t) / L_t
    return float(v_t), float(w_t)

def _read_twist(entity) -> Optional[Tuple[float,float]]:
    """Try common twist fields: linear.x and angular.z (ROS-style)."""
    try:
        if entity is not None:
            Vl = getattr(entity, "v_signed", None)
            Vw = getattr(entity, "w", None)
            if Vl is not None and Vw is not None:
                return float(Vl), float(Vw)
    except Exception:
        pass
    return None

def _read_pose(entity) -> Optional[Tuple[float,float,float]]:
    """Try common pose fields (x,y,yaw) or pose.position + pose.orientation quaternion -> yaw."""
    try:
        pose = getattr(entity, "pose", None)
        if pose is not None:
            pos = getattr(pose, "position", None) or pose
            x = getattr(pos, "x", None) or getattr(pos, 0, None)
            y = getattr(pos, "y", None) or getattr(pos, 1, None)
            orient = getattr(pose, "orientation", None)
            if orient is not None:
                qx = getattr(orient, "x", 0.0)
                qy = getattr(orient, "y", 0.0)
                qz = getattr(orient, "z", 0.0)
                qw = getattr(orient, "w", 1.0)
                siny = 2.0*(qw*qz + qx*qy)
                cosy = 1.0 - 2.0*(qy*qy + qz*qz)
                yaw = np.atan2(siny, cosy)
            else:
                yaw = getattr(pose, "theta", None) or getattr(pose, "yaw", None) or getattr(pose, 2, None)
            if x is not None and y is not None and yaw is not None:
                return float(x), float(y), float(yaw)
        # fallback direct attrs
        x = getattr(entity, "x", None); y = getattr(entity, "y", None); yaw = getattr(entity, "theta", None)
        if x is not None and y is not None and yaw is not None:
            return float(x), float(y), float(yaw)
    except Exception:
        pass
    return None

class DataCollector:
    """
    Coleta pares de (comando de referência, comando atuado) para criar o dataset.
    """
    def __init__(self, world, filename="DataSetTest.csv"):
        self._collect_prev = (0,0)
        self.world = world
        self.filename = filename

    def collect(self, wL_s: float, wR_s: float, r_t: Optional[float]=r, L_t: Optional[float]=L, dt_fallback: float=0.016, settle_seconds: float=0.0):
        """
        Minimal data collector. Writes CSV rows:
        wL_s,wR_s,r_t,L_t,v_gt,w_gt,timestamp
        Caller is responsible for issuing the wheel commands before calling collect and (optionally) waiting a short time.
        """

        # optional settle
        if settle_seconds > 0:
            time.sleep(settle_seconds)

        # find entity
        try:
            entity = self.world.team[0].entity
        except Exception:
            entity = getattr(self.world.team[0], "entity", None)
        if entity is None:
            return  # nothing to log

        ts = time.time()

        # 1) try to read twist directly
        v = _read_twist(entity)
        if v is not None:
            v_gt, w_gt = v
        else:
            # 2) fallback: finite-difference on pose; store prev on self._collect_prev
            pose = _read_pose(entity)
            if pose is None:
                raise RuntimeError("collect(): cannot read twist or pose from simulator entity")
            prev = getattr(self, "_collect_prev", None)
            if prev is None:
                # store and skip this call (need next sample to compute velocities)
                self._collect_prev = (pose, ts)
                return
            (x_prev, y_prev, th_prev), t_prev = prev
            x_curr, y_curr, th_curr = pose
            dt = ts - t_prev if (ts - t_prev) > 1e-6 else dt_fallback
            dx = x_curr - x_prev; dy = y_curr - y_prev
            forward = dx * np.cos(th_prev) + dy * np.sin(th_prev)
            v_gt = forward / dt
            dth = th_curr - th_prev
            dth = (dth + np.pi) % (2*np.pi) - np.pi
            w_gt = dth / dt
            self._collect_prev = (pose, ts)

        # write CSV (create header once)
        header = "wL_s,wR_s,r_t,L_t,v_gt,w_gt,timestamp\n"
        need_header = not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0
        line = f"{wL_s:.10f},{wR_s:.10f},{r_t:.10f},{L_t:.10f},{v_gt:.10f},{w_gt:.10f},{ts:.6f}\\n"
        with open(self.filename, "a") as f:
            if need_header:
                f.write(header)
            f.write(line)
            f.flush()
                
class ResidualMapper(nn.Module):
    def __init__(self, in_dim=4, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
        nn.Linear(in_dim, hidden),
        nn.ReLU(),
        nn.Linear(hidden, hidden),
        nn.ReLU(),
        nn.Linear(hidden, 2) # delta v, delta w
    )
    def forward(self, x):
        return self.net(x)

    # training loop (very compact)

    # v_s, w_s (AI)
    # r_s, L_s (AI)
    # r_t, L_t (UnBrain)
    # x: [wL_s, wR_s, r_t, L_t]
    # baseline from analytic_transform -> v_analytic, w_analytic
    # target GT in dataset: v_gt, w_gt
    # loss = MSE((v_analytic + dv) , v_gt) + MSE((w_analytic + dw), w_gt)

def train_residual(
    model: nn.Module,
    dataset: np.ndarray,
    epochs: int = 200,
    batch_size: int = 256,
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    device: str = "cuda",
    verbose: bool = True,
) -> Dict[str, Any]:
    """Train residual model on a dataset.
    dataset rows expected to be: [wL_s, wR_s, r_t, L_t, v_gt, w_gt]
    The model predicts dv, dw to be added to analytic transform.
    Loss = MSE((v_analytic + dv), v_gt) + MSE((w_analytic + dw), w_gt)
    """
    model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.MSELoss()

    X = dataset[:, :4].astype(np.float32)
    Y = dataset[:, 4:6].astype(np.float32)
    n = len(X)
    history = {"loss": []}

    tensor_X = torch.from_numpy(X).to(device)
    tensor_Y = torch.from_numpy(Y).to(device)

    for epoch in range(epochs):
        perm = np.random.permutation(n)
        epoch_loss = 0.0
        for i in range(0, n, batch_size):
            idx = perm[i : i + batch_size]
            xb = tensor_X[idx]
            yb = tensor_Y[idx]
            # compute analytic baseline
            with torch.no_grad():
                wL_s = xb[:, 0]
                wR_s = xb[:, 1]
                r_t = xb[:, 2]
                L_t = xb[:, 3]
                # analytic transform vectorized
                vL_t = wL_s * r_t
                vR_t = wR_s * r_t
                v_analytic = 0.5 * (vL_t + vR_t)
                w_analytic = (vR_t - vL_t) / L_t
                analytic = torch.stack([v_analytic, w_analytic], dim=1)
            optimizer.zero_grad()
            dv_dw = model(xb)
            pred = analytic + dv_dw
            loss = loss_fn(pred, yb)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * xb.size(0)
        
        epoch_loss /= n
        history["loss"].append(epoch_loss)
        if verbose and (epoch % max(1, epochs // 10) == 0 or epoch == epochs - 1):
            print(f"Epoch {epoch+1}/{epochs} loss={epoch_loss:.6f}")
    
    return history

def load_residual(model: nn.Module, path: str, device: str = "cuda") -> nn.Module:
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    return model

def predict_with_residual(
    model: nn.Module,
    wL_s: float,
    wR_s: float,
    r_t: float,
    L_t: float,
    device: str = "cuda",
) -> Tuple[float, float]:
    """Compute analytic transform and apply residual correction from model."""
    v_a, w_a = analytic_transform(wL_s, wR_s, r_t, L_t)
    x = np.array([wL_s, wR_s, r_t, L_t], dtype=np.float32)
    tensor_x = torch.from_numpy(x).unsqueeze(0).to(device)
    with torch.no_grad():
        dv_dw = model(tensor_x).cpu().numpy().squeeze(0)
    v_t = float(v_a + dv_dw[0])
    w_t = float(w_a + dv_dw[1])
    return v_t, w_t

def estimate_effective_r_L(data: np.ndarray) -> Tuple[float, float]:
    """Estimate effective wheel radius r_eff and wheelbase L_eff from calibration data.

    Expected data rows: [v_cmd, w_cmd, measured_v, measured_w]
    where v_cmd, w_cmd are commands sent to the robot (body frame) and measured_v, measured_w
    are the resulting body velocities observed.

    We solve for scalars alpha_r and alpha_L such that applying the analytic transform with
    r'=alpha_r * r_nom and L'=alpha_L * L_nom best fits measured results. Because r_nom and L_nom
    might not be present in the calibration set, we instead formulate:

    measured_v = s1 * v_cmd + s2 * w_cmd
    measured_w = s3 * v_cmd + s4 * w_cmd

    and solve for the 4 coefficients via least squares; then compute approximate effective r,L
    if the nominal geometry is known. This function returns derived scaling terms (not guaranteed
    to map directly to physical r,L in the presence of dynamics) but is often useful.

    Returns (s_v_v, s_v_w) as a simple linear mapping predictor if full r,L not derivable.
    For simplicity we return two scalars that map [v_cmd, w_cmd] -> measured_v (best fit), and
    two scalars that map -> measured_w. Callers can derive ad-hoc r/L adjustments from them.

    Args:
    data: numpy array shape (N,4)

    Returns:
    tuple: (a1, a2, a3, a4) where measured_v ~= a1*v_cmd + a2*w_cmd;
    measured_w ~= a3*v_cmd + a4*w_cmd
    """
    assert data.shape[1] == 4, "data must have shape (N,4): v_cmd, w_cmd, measured_v, measured_w"
    V = data[:, :2] # commands
    Y = data[:, 2:4] # measurements
    # Solve for A 2x2 matrix such that V @ A.T ~= Y
    # Using least-squares for each output dimension
    A, *_ = np.linalg.lstsq(V, Y, rcond=None)
    # A is 2x2 (columns correspond to outputs) -> return flattened
    a1, a3 = A[0, 0], A[0, 1]
    a2, a4 = A[1, 0], A[1, 1]
    # Return in an intuitive order: a1, a2, a3, a4 s.t.
    # measured_v = a1*v_cmd + a2*w_cmd
    # measured_w = a3*v_cmd + a4*w_cmd
    return float(a1), float(a2), float(a3), float(a4)

def generate_synthetic_dataset(
    n: int = 10000,
    wL_s_range: Tuple[float, float] = (-20.0, 20.0),
    wR_s_range: Tuple[float, float] = (-20.0, 20.0),
    r_t: Tuple[float, float] = (0.03, 0.06),
    L_t: Tuple[float, float] = (0.12, 0.3),
    noise_std: float = 0.01,
    dynamics_bias: float = 0.0,
    seed: int = 42
) -> np.ndarray:
    """Create a synthetic dataset of mappings from source commands to target observed body velocities.
    Each row: [wL_s, wR_s, r_t, L_t, v_gt, w_gt]
    The "ground truth" mapping is generated by applying the analytic transform and then adding
    configurable noise and optional dynamics biases to emulate sim differences.
    """
    rng = np.random.RandomState(seed)
    wL_arr = rng.uniform(wL_s_range[0], wL_s_range[1], size=n)
    wR_arr = rng.uniform(wR_s_range[0], wR_s_range[1], size=n)
    r_t_vals = rng.uniform(r_t[0], r_t[1], size=n)
    L_t_vals = rng.uniform(L_t[0], L_t[1], size=n)
    rows = []
    for i in range(n):
        wL_s_val = float(wL_arr[i])
        wR_s_val = float(wR_arr[i])
        rt = float(r_t_vals[i])
        Lt = float(L_t_vals[i])
        # analytic baseline
        va, wa = analytic_transform(wL_s_val, wR_s_val, rt, Lt)
        # simulate dynamics differences: small nonlinear bias + noise
        # example bias: scale linear velocity slightly and add coupling from angular velocity
        v_bias = va * (1.0 + dynamics_bias * rng.randn()) + 0.02 * wL_s_val
        w_bias = wa * (1.0 + dynamics_bias * rng.randn()) + 0.01 * wR_s_val
        v_gt = v_bias + rng.normal(0.0, noise_std)
        w_gt = w_bias + rng.normal(0.0, noise_std)
        rows.append([wL_s_val, wR_s_val, rt, Lt, v_gt, w_gt])
    
    return np.array(rows, dtype=np.float32)

def map_command(
    wL_s: float,
    wR_s: float,
    r_t: float,
    L_t: float,
    residual_model: Optional[Any] = None,
    device: str = "cuda",
) -> Tuple[float, float]:
    """Map source command to target command. If residual_model provided (PyTorch model), it will
    be used to correct analytic output. Otherwise analytic-only mapping is used.
    The external loop can call this function at runtime for each commanded pair.
    """
    v_a, w_a = analytic_transform(wL_s, wR_s, r_t, L_t)
    if residual_model is None:
        return v_a, w_a
    return predict_with_residual(residual_model, wL_s, wR_s, r_t, L_t, device=device)

def integrate_pose(commands: np.ndarray, dt: float = 0.02) -> np.ndarray:
    """Integrate a sequence of body commands into poses (x,y,theta).
    commands: array shape (T,2) containing [v, w]
    returns: poses array shape (T+1, 3)
    """
    T = len(commands)
    poses = np.zeros((T + 1, 3), dtype=float)
    x, y, th = 0.0, 0.0, 0.0
    poses[0] = [x, y, th]
    for i in range(T):
        v, w = float(commands[i, 0]), float(commands[i, 1])
        # simple Euler integration
        dx = v * np.cos(th) * dt
        dy = v * np.sin(th) * dt
        dth = w * dt
        x += dx
        y += dy
        th += dth
        poses[i + 1] = [x, y, th]
    return poses

def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))

def demo_training_pipeline():
    """Demonstration function that creates synthetic data, trains residual and evaluates.
    Not executed on import; caller may invoke it.
    """

    print("Generating synthetic dataset...")
    data = generate_synthetic_dataset(n=5000)
    print("Dataset shape:", data.shape)

    # split
    n = len(data)
    idx = np.random.permutation(n)
    train_idx = idx[: int(0.9 * n)]
    val_idx = idx[int(0.9 * n) :]
    train_set = data[train_idx]
    val_set = data[val_idx]

    model = ResidualMapper()
    print("Training residual model...")
    history = train_residual(model, train_set, epochs=100, batch_size=256, verbose=True)

    # quick eval on val set
    X_val = val_set[:, :4]
    Y_val = val_set[:, 4:6]
    preds = []
    for row in X_val:
        wL_s, wR_s, r_t, L_t = row.tolist()
        v_p, w_p = predict_with_residual(model, wL_s, wR_s, r_t, L_t)
        preds.append([v_p, w_p])
    preds = np.array(preds)
    print("Val MSE:", mse(preds, Y_val))

    return model, history

if __name__ == "__main__":
    # quick smoke test (analytic-only)
    wL_s, wR_s = 0.5, 0.2
    r_t, L_t = r, L
    v_t, w_t = analytic_transform(wL_s, wR_s, r_t, L_t)
    print(f"Analytic transform -> v_t={v_t:.4f}, w_t={w_t:.4f}")
    data = generate_synthetic_dataset(
        n=5000000,
        wL_s_range=(-10,10),
        wR_s_range=(-10,10),
        r_t=(0.04,0.05),
        L_t=(0.18,0.22),
        noise_std=0.005,
        dynamics_bias=0.01)
    print("dataset shape:", data.shape)
    print("first row:", data[0])