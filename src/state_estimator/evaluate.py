import torch
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import os

# Adicionar caminhos para importar os filtros originais do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_system', 'controller')))
from tools.kalman import KalmanFilter, KalmanFilterAngular

from neural_estimator import NeuralStateEstimator
from generate_dataset import generate_kinematic_trajectory, apply_domain_randomization

def calculate_rmse(predictions, ground_truth):
    """Calcula o Root Mean Squared Error (RMSE)."""
    return np.sqrt(np.mean((predictions - ground_truth) ** 2))

def calculate_angular_rmse(predictions, ground_truth):
    """Calcula o RMSE para ângulos respeitando a descontinuidade em pi."""
    diff = (predictions - ground_truth + np.pi) % (2 * np.pi) - np.pi
    return np.sqrt(np.mean(diff ** 2))

def evaluate():
    print("Iniciando Pipeline de Benchmarking...")
    
    # 1. Gerar dados de teste NUNCA vistos (1 trajetória longa)
    steps = 2000
    dt = 0.016 # 60Hz
    true_states, actions = generate_kinematic_trajectory(steps=steps, dt=dt)
    noisy_states = apply_domain_randomization(true_states)
    
    # Adicionar atraso na visão (ex: 3 frames = ~48ms) para simular lag da câmera
    delay_frames = 3
    delayed_vision = np.zeros_like(noisy_states)
    delayed_vision[delay_frames:] = noisy_states[:-delay_frames]
    delayed_vision[:delay_frames] = noisy_states[0]

    # EMA removido para não induzir Phase Lag no Neural Estimator

    # 2. Instanciar Filtros
    # A) Kalman 1D Legado (X, Y, Theta) - Usa raw vision
    kf_x = KalmanFilter()
    kf_x.setInitialPos(delayed_vision[0, 0])
    
    kf_y = KalmanFilter()
    kf_y.setInitialPos(delayed_vision[0, 1])
    
    kf_th = KalmanFilterAngular()
    kf_th.setInitialPos(delayed_vision[0, 2])

    # B) Neural Estimator
    history_size = 10
    hidden_dim = 64
    
    # Tentar carregar best_params.json se existir
    import json
    if os.path.exists("best_params.json"):
        with open("best_params.json", "r") as f:
            best_params = json.load(f)
            history_size = best_params.get("history_size", 10)
            hidden_dim = best_params.get("hidden_dim", 64)
            print(f"Carregado best_params.json: history={history_size}, hidden={hidden_dim}")
            
    neural_model = NeuralStateEstimator(history_size=history_size, hidden_dim=hidden_dim)
    neural_model.eval()
    
    # Se houver pesos, podemos tentar carregá-los. Mas para fins de avaliação offline
    # mesmo um modelo com pesos curtos (ou até aleatório para provar o pipeline) rodará.
    if os.path.exists("best_sim2real_model.pth"):
        try:
            neural_model.load_state_dict(torch.load("best_sim2real_model.pth", map_location="cpu"))
            print("Carregados pesos de best_sim2real_model.pth")
        except Exception as e:
            print("Não foi possível carregar os pesos (arquitetura diferente?). Usando inicialização padrão.")
    else:
        print("Aviso: 'best_sim2real_model.pth' não encontrado. Usando pesos iniciais.")

    # Listas para guardar histórico de predição
    kalman_preds = []
    neural_preds = []
    
    # Estado inicial (histórico de buffer circular para a rede) usando raw
    vision_buffer = np.zeros((history_size, 9))
    for i in range(history_size):
        sin_init = math.sin(delayed_vision[0, 2])
        cos_init = math.cos(delayed_vision[0, 2])
        vision_buffer[i] = [delayed_vision[0, 0], delayed_vision[0, 1], sin_init, cos_init, actions[0, 0], actions[0, 1], 0.0, 0.0, 0.0]
    
    print("Correndo a corrida frame a frame...")
    for t in range(steps):
        # Medição atual
        raw_x = delayed_vision[t, 0]
        raw_y = delayed_vision[t, 1]
        raw_th = delayed_vision[t, 2]
        
        z_x = raw_x
        z_y = raw_y
        z_th = raw_th
        
        # 1. Atualizar Kalman
        pred_kx = kf_x.estimate(np.array([[raw_x]]), dt)[0, 0]
        pred_ky = kf_y.estimate(np.array([[raw_y]]), dt)[0, 0]
        pred_kth = kf_th.estimate(np.array([[raw_th]]), dt)[0, 0]
        kalman_preds.append([pred_kx, pred_ky, pred_kth])
        
        # 2. Atualizar Neural
        # Usar a mesma política do `generate_dataset.py` (usando a ação do frame atual t)
        v_cmd = actions[t, 0]
        w_cmd = actions[t, 1]
        
        raw_th_wrapped = (raw_th + math.pi) % (2 * math.pi) - math.pi
        sin_th = math.sin(raw_th_wrapped)
        cos_th = math.cos(raw_th_wrapped)
            
        # Shift buffer (remove o mais velho, adiciona o novo)
        vision_buffer = np.roll(vision_buffer, shift=-1, axis=0)
        dt_kin = 0.016
        dx_kin = v_cmd * cos_th * dt_kin
        dy_kin = v_cmd * sin_th * dt_kin
        dtheta_kin = w_cmd * dt_kin
        vision_buffer[-1] = [raw_x, raw_y, sin_th, cos_th, v_cmd, w_cmd, dx_kin, dy_kin, dtheta_kin]
        
        # Inferência Neural
        with torch.no_grad():
            tensor_input = torch.tensor(vision_buffer, dtype=torch.float32).unsqueeze(0)
            pred_residual = neural_model(tensor_input).squeeze(0).numpy()
            
            # Bug 2 fix: O resíduo soma-se à visão mais recente do buffer
            last_x = vision_buffer[-1, 0]
            last_y = vision_buffer[-1, 1]
            last_th = math.atan2(vision_buffer[-1, 2], vision_buffer[-1, 3])
            
            x_final = last_x + pred_residual[0]
            y_final = last_y + pred_residual[1]
            th_final = last_th + pred_residual[2]
            
            # Normalização do ângulo
            th_final = (th_final + math.pi) % (2 * math.pi) - math.pi
            
            pred_neural = np.array([x_final, y_final, th_final])
            
        neural_preds.append(pred_neural)

    kalman_preds = np.array(kalman_preds)
    neural_preds = np.array(neural_preds)
    
    # 3. Matemática: Calcular RMSE (ignorando primeiros frames de warmup)
    warmup = max(history_size, 100)
    
    # Avaliar contra t+2 (Previsão de Futuro / Dead Time Compensation)
    forecast = 2
    rmse_kalman_x = calculate_rmse(kalman_preds[warmup:-forecast, 0], true_states[warmup+forecast:, 0])
    rmse_kalman_y = calculate_rmse(kalman_preds[warmup:-forecast, 1], true_states[warmup+forecast:, 1])
    rmse_kalman_th = calculate_angular_rmse(kalman_preds[warmup:-forecast, 2], true_states[warmup+forecast:, 2])
    
    rmse_neural_x = calculate_rmse(neural_preds[warmup:-forecast, 0], true_states[warmup+forecast:, 0])
    rmse_neural_y = calculate_rmse(neural_preds[warmup:-forecast, 1], true_states[warmup+forecast:, 1])
    rmse_neural_th = calculate_angular_rmse(neural_preds[warmup:-forecast, 2], true_states[warmup+forecast:, 2])
    
    avg_rmse_kalman = (rmse_kalman_x + rmse_kalman_y + rmse_kalman_th*0.1) / 3.0 # Peso menor pro ângulo
    avg_rmse_neural = (rmse_neural_x + rmse_neural_y + rmse_neural_th*0.1) / 3.0
    
    melhoria_x = (rmse_kalman_x - rmse_neural_x) / rmse_kalman_x * 100
    melhoria_y = (rmse_kalman_y - rmse_neural_y) / rmse_kalman_y * 100
    melhoria_th = (rmse_kalman_th - rmse_neural_th) / rmse_kalman_th * 100
    
    print("\n" + "="*50)
    print("RELATÓRIO DE BENCHMARKING (RMSE)")
    print("="*50)
    print(f"Eixo X     - Kalman: {rmse_kalman_x:.4f} | Neural: {rmse_neural_x:.4f} (Melhoria: {melhoria_x:.1f}%)")
    print(f"Eixo Y     - Kalman: {rmse_kalman_y:.4f} | Neural: {rmse_neural_y:.4f} (Melhoria: {melhoria_y:.1f}%)")
    print(f"Eixo Theta - Kalman: {rmse_kalman_th:.4f} | Neural: {rmse_neural_th:.4f} (Melhoria: {melhoria_th:.1f}%)")
    
    total_melhoria = (avg_rmse_kalman - avg_rmse_neural) / avg_rmse_kalman * 100
    print("-" * 50)
    print(f"Neural Estimator reduziu o erro médio global em {total_melhoria:.1f}% face ao Kalman.")
    print("="*50)

    # 4. Prova Visual: Gerar Gráficos Matplotlib
    print("\nA gerar visualização trajectory_comparison.png...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Plot 1: Visão Macro (Trajetória Completa)
    ax1.set_title("Visão Macro: Trajetória Completa (X vs Y)")
    ax1.scatter(delayed_vision[:, 0], delayed_vision[:, 1], c='blue', s=2, alpha=0.3, label='Visão Ruidosa (Câmera)')
    ax1.plot(true_states[:, 0], true_states[:, 1], 'k--', linewidth=1.5, label='Ground Truth')
    ax1.plot(kalman_preds[:, 0], kalman_preds[:, 1], 'r-', linewidth=1, label='Kalman Filter Legado')
    ax1.plot(neural_preds[:, 0], neural_preds[:, 1], 'g-', linewidth=1, label='Neural Estimator')
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.7)
    
    # Plot 2: Visão Micro (Zoom-in janela de alta dinâmica)
    # Procurar um ponto onde houve grande variação
    velocities = np.sqrt(np.diff(true_states[:, 0])**2 + np.diff(true_states[:, 1])**2)
    start_zoom = np.argmax(velocities[100:1000]) + 100 # Encontrar uma curva rápida
    end_zoom = start_zoom + 150 # Janela de 150 frames
    
    ax2.set_title(f"Visão Micro: Phase Lag (Frames {start_zoom}-{end_zoom})")
    ax2.scatter(delayed_vision[start_zoom:end_zoom, 0], delayed_vision[start_zoom:end_zoom, 1], c='blue', s=10, alpha=0.5, label='Visão Ruidosa')
    ax2.plot(true_states[start_zoom:end_zoom, 0], true_states[start_zoom:end_zoom, 1], 'k-o', markersize=3, label='Ground Truth')
    ax2.plot(kalman_preds[start_zoom:end_zoom, 0], kalman_preds[start_zoom:end_zoom, 1], 'r-x', markersize=3, label='Kalman Filter')
    ax2.plot(neural_preds[start_zoom:end_zoom, 0], neural_preds[start_zoom:end_zoom, 1], 'g-^', markersize=3, label='Neural Estimator')
    ax2.set_xlabel("X (m)")
    ax2.set_ylabel("Y (m)")
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig("trajectory_comparison.png", dpi=150)
    print("Gráfico salvo como 'trajectory_comparison.png'")

if __name__ == "__main__":
    evaluate()
