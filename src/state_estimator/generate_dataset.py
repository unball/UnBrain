import torch
import numpy as np
import pandas as pd
import random
import math
import os

def generate_kinematic_trajectory(steps=1000, dt=0.016):
    """
    Gera uma trajetória baseada no modelo cinemático de uniciclo.
    """
    x, y, theta = 0.0, 0.0, 0.0
    # Estado inicial: robô no centro
    x, y, theta = 0.0, 0.0, 0.0
    states = []
    actions = []
    
    # Randomizar frequências e amplitudes para cada trajetória gerada!
    # Isto garante que a rede não overfitta num caminho único determinístico,
    # e que aprende a cinemática física real (sem ruído irreal em alta frequência).
    v_freq = random.uniform(0.01, 0.08)
    w_freq = random.uniform(0.01, 0.05)
    v_amp = random.uniform(0.5, 1.5)
    w_amp = random.uniform(2.0, 6.0)
    
    for _ in range(steps):
        # Ações de controle suaves, mas com diversidade massiva entre trajetórias
        v = math.sin(_ * v_freq) * v_amp
        w = math.cos(_ * w_freq) * w_amp
        
        # Evitar colisões com a parede suavemente para NÃO quebrar a cinemática
        # Área Jogável: 1.5x1.3 (0.75 em X, 0.65 em Y). Margem de segurança = 0.13m (13cm)
        is_outside = False
        goal_half_width = 0.20
        margin = 0.13
        if abs(y) <= goal_half_width:
            if abs(x) > 0.875 - margin:
                is_outside = True
        else:
            if abs(x) > 0.75 - margin or abs(y) > 0.65 - margin:
                is_outside = True
                
        if is_outside:
            # Força o w a apontar de volta para o centro (0,0)
            angle_to_center = math.atan2(-y, -x)
            angle_diff = (angle_to_center - theta + math.pi) % (2 * math.pi) - math.pi
            w = angle_diff * 3.0 + random.uniform(-0.5, 0.5)
            
        # Atualização cinemática pura (Causalidade Mantida)
        x += v * math.cos(theta) * dt
        y += v * math.sin(theta) * dt
        theta += w * dt
        
        # Simular colisão física com a parede (clamping rígido)
        # Se bater na parede, as rodas giram (v comando) mas a posição real não avança!
        if abs(y) <= goal_half_width:
            x = np.clip(x, -0.875, 0.875)
        else:
            x = np.clip(x, -0.75, 0.75)
        
        y = np.clip(y, -0.675, 0.675)
        
        # Normalizar theta para [-pi, pi]
        theta = (theta + math.pi) % (2 * math.pi) - math.pi
        
        states.append((x, y, theta))
        actions.append((v, w))
        
    return np.array(states), np.array(actions)

def apply_domain_randomization(states):
    """
    Aplica ruído Gaussiano variável (Domain Randomization) simulando 
    diferentes condições de iluminação e câmeras desfocadas.
    Retorna os estados com ruído.
    """
    noisy_states = np.copy(states)
    
    # Variância do ruído aleatória por episódio
    std_x = random.uniform(0.001, 0.02)
    std_y = random.uniform(0.001, 0.02)
    std_th = random.uniform(0.01, 0.1)
    
    noise = np.random.normal(loc=0.0, scale=[std_x, std_y, std_th], size=states.shape)
    noisy_states += noise
    
    # Dropout (simulando falha do tracker e perda de pacote)
    dropout_prob = random.uniform(0.01, 0.05)
    mask = np.random.rand(states.shape[0]) < dropout_prob
    
    # Quando há dropout, o tracker normalmente congela no frame anterior
    for i in range(1, states.shape[0]):
        if mask[i]:
            noisy_states[i] = noisy_states[i-1]
            
    return noisy_states

def build_dataset(num_trajectories=100, steps_per_traj=1000, history_size=10, val_split=0.15):
    X_train, Y_train = [], []
    X_val, Y_val = [], []
    
    predict_ahead = 2
    dt_step = 0.016
    
    print("Gerando dataset de trajetórias com Domain Randomization (Sim-to-Real)...")
    
    num_val = int(num_trajectories * val_split)
    
    for i in range(num_trajectories):
        is_val = i < num_val
        true_states, actions = generate_kinematic_trajectory(steps=steps_per_traj)
        
        # O histórico de visão que o robô enxerga é o true_state com ruído
        noisy_states = apply_domain_randomization(true_states)
        
        # Delay aleatório neste episódio (1 a 5 frames, equivale a ~16ms a ~80ms)
        delay_frames = random.randint(1, 5)
        
        # Array final simulando o que a câmera reportou (já com atraso)
        delayed_vision = np.zeros_like(noisy_states)
        delayed_vision[delay_frames:] = noisy_states[:-delay_frames]
        # Os primeiros frames não têm visão válida ainda
        delayed_vision[:delay_frames] = noisy_states[0]
        
        # REMOVIDO: EMA FILTER. O modelo operará nos dados brutos.
        
        # Construir as janelas deslizantes (Sliding Windows)
        for t in range(history_size, steps_per_traj):
            # Histórico: últimos 'history_size' frames
            window_vision = delayed_vision[t-history_size:t]
            window_actions = actions[t-history_size:t]
            
            # Converter theta para sin(theta) e cos(theta) na visão
            window_vision_x = window_vision[:, 0:1]
            window_vision_y = window_vision[:, 1:2]
            window_vision_th = window_vision[:, 2:3]
            sin_th = np.sin(window_vision_th)
            cos_th = np.cos(window_vision_th)
            
            # PINN - Física (Delta Cinemático Esperado)
            v_cmd = window_actions[:, 0:1]
            w_cmd = window_actions[:, 1:2]
            dt = 0.016
            dx_kin = v_cmd * cos_th * dt
            dy_kin = v_cmd * sin_th * dt
            dtheta_kin = w_cmd * dt
            
            # Features (history_size, 9): [x_cam, y_cam, sin_th, cos_th, v_cmd, w_cmd, dx_kin, dy_kin, dtheta_kin]
            window_features = np.concatenate([window_vision_x, window_vision_y, sin_th, cos_th, v_cmd, w_cmd, dx_kin, dy_kin, dtheta_kin], axis=1)
            
            future_t = min(t + predict_ahead, steps_per_traj - 1)
            
            # Target: Estado FUTURO real (Residual Learning)
            residual_x = true_states[future_t, 0] - window_vision[-1, 0]
            residual_y = true_states[future_t, 1] - window_vision[-1, 1]
            residual_th = true_states[future_t, 2] - window_vision[-1, 2]
            
            # Normalização circular do ângulo para o erro (Evita que o erro pule de -pi para pi)
            residual_th = (residual_th + math.pi) % (2 * math.pi) - math.pi
            
            # Adicionar derivadas reais (velocidades absolutas) ao target para o PPO:
            dt_step = 0.016
            vx_real = (true_states[future_t, 0] - true_states[future_t-1, 0]) / dt_step
            vy_real = (true_states[future_t, 1] - true_states[future_t-1, 1]) / dt_step
            
            w_real_diff = (true_states[future_t, 2] - true_states[future_t-1, 2] + math.pi) % (2 * math.pi) - math.pi
            w_real = w_real_diff / dt_step
            
            target_state = np.array([residual_x, residual_y, residual_th, vx_real, vy_real, w_real], dtype=np.float32)            
            
            if is_val:
                X_val.append(window_features)
                Y_val.append(target_state)
            else:
                X_train.append(window_features)
                Y_train.append(target_state)
                
    return (np.array(X_train, dtype=np.float32), np.array(Y_train, dtype=np.float32),
            np.array(X_val, dtype=np.float32), np.array(Y_val, dtype=np.float32),
            predict_ahead, dt_step)

if __name__ == "__main__":
    history_sz = 15
    X_train, Y_train, X_val, Y_val, p_ahead, dt = build_dataset(num_trajectories=200, steps_per_traj=500, history_size=history_sz)
    print(f"Dataset shape: Train X={X_train.shape}, Val X={X_val.shape}")
    
    # Salvar em formato binário eficiente com os metadata
    os.makedirs("data", exist_ok=True)
    
    dataset_dict = {
        "X_train": torch.tensor(X_train), "Y_train": torch.tensor(Y_train),
        "X_val": torch.tensor(X_val), "Y_val": torch.tensor(Y_val),
        "metadata": {
            "history_size": history_sz,
            "predict_ahead": p_ahead,
            "dt": dt
        }
    }
    
    torch.save(dataset_dict, "data/sim2real_dataset.pt")
    print("Dataset e Metadata salvos em data/sim2real_dataset.pt")
