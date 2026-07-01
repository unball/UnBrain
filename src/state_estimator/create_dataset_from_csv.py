import torch
import numpy as np
import pandas as pd
import random
import math
import os
from generate_dataset import apply_domain_randomization

def build_dataset_from_csv(csv_path="/home/maranhas/UnBall/UnBrain/src/state_estimator/data", history_size=10):
    df = pd.read_csv(csv_path, names=["t", "r_id", "raw_x", "raw_y", "raw_th", "v_signed", "angvel"])
    
    X = []
    Y = []
    
    for r_id in df['r_id'].unique():
        df_robot = df[df['r_id'] == r_id].sort_values("t")
        
        true_states = df_robot[['raw_x', 'raw_y', 'raw_th']].values
        actions = df_robot[['v_signed', 'angvel']].values
        
        if len(true_states) <= history_size:
            continue
            
        # Aplica Domain Randomization aos "true states" provindos do FiraSim (que servem de Ground Truth)
        noisy_states = apply_domain_randomization(true_states)
        
        # Delay aleatório (1 a 5 frames)
        delay_frames = random.randint(1, 5)
        
        delayed_vision = np.zeros_like(noisy_states)
        delayed_vision[delay_frames:] = noisy_states[:-delay_frames]
        delayed_vision[:delay_frames] = noisy_states[0]
        
        for t in range(history_size, len(true_states)):
            window_vision = delayed_vision[t-history_size:t]
            window_actions = actions[t-history_size:t]
            
            window_vision_x = window_vision[:, 0:1]
            window_vision_y = window_vision[:, 1:2]
            window_vision_th = window_vision[:, 2:3]
            sin_th = np.sin(window_vision_th)
            cos_th = np.cos(window_vision_th)
            
            # Features (history_size, 6): [x_cam, y_cam, sin_th, cos_th, v_cmd, w_cmd]
            window_features = np.concatenate([window_vision_x, window_vision_y, sin_th, cos_th, window_actions], axis=1)
            
            # Target Residual
            residual_x = true_states[t, 0] - window_vision[-1, 0]
            residual_y = true_states[t, 1] - window_vision[-1, 1]
            residual_th = true_states[t, 2] - window_vision[-1, 2]
            residual_th = (residual_th + math.pi) % (2 * math.pi) - math.pi
            
            target_state = np.array([residual_x, residual_y, residual_th], dtype=np.float32)
            
            X.append(window_features)
            Y.append(target_state)
            
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "../../data/sim2real_recorded_data.csv"
    if not os.path.exists(csv_path):
        print(f"Erro: {csv_path} não encontrado!")
        sys.exit(1)
        
    X, Y = build_dataset_from_csv(csv_path)
    print(f"Dataset shape: X={X.shape}, Y={Y.shape}")
    
    os.makedirs("data", exist_ok=True)
    torch.save({"X": torch.tensor(X), "Y": torch.tensor(Y)}, "data/sim2real_dataset.pt")
    print("Dataset salvo em data/sim2real_dataset.pt")
    print("Agora pode executar: python train.py")
