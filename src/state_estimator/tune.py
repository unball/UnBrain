import optuna
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os
import json

from neural_estimator import NeuralStateEstimator
from generate_dataset import build_dataset

def ensure_hpo_dataset(max_history=15):
    dataset_path = f"data/sim2real_dataset_hpo_h{max_history}.pt"
    if not os.path.exists(dataset_path):
        print(f"Gerando dataset de HPO com history_size={max_history}...")
        X, Y = build_dataset(num_trajectories=200, steps_per_traj=500, history_size=max_history)
        os.makedirs("data", exist_ok=True)
        torch.save({"X": torch.tensor(X), "Y": torch.tensor(Y)}, dataset_path)
    return dataset_path

def objective(trial):
    # 1. Sugerir hiperparâmetros
    lr = trial.suggest_float("learning_rate", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128, 256])
    history_size = trial.suggest_int("history_size", 3, 15)
    hidden_dim = trial.suggest_categorical("hidden_dim", [32, 64, 128])
    epochs = 5 # Menos épocas para teste rápido
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 2. Carregar os dados (já com history máximo = 15)
    dataset_path = ensure_hpo_dataset(max_history=15)
    data = torch.load(dataset_path, map_location="cpu")
    
    # Selecionar apenas os últimos `history_size` frames da janela temporal
    X_tensor = data["X"][:, -history_size:, :]
    Y_tensor = data["Y"]
    
    dataset = TensorDataset(X_tensor, Y_tensor)
    
    # Train / Val Split (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 3. Instanciar Modelo e Otimizador
    model = NeuralStateEstimator(history_size=history_size, hidden_dim=hidden_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.SmoothL1Loss(beta=0.1)
    
    # 4. Loop de Treino
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            
    # 5. Avaliação (Validation Loss)
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            val_loss += loss.item() * batch_x.size(0)
            
    val_loss /= len(val_dataset)
    return val_loss

def run_optimization(n_trials=100):
    print("Iniciando Otimização de Hiperparâmetros (HPO) com Optuna...")
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    
    print("\nOtimização concluída!")
    print("Melhores parâmetros encontrados:")
    best_params = study.best_params
    for key, value in best_params.items():
        print(f"  {key}: {value}")
    print(f"  Melhor Val Loss: {study.best_value}")
    
    # Salvar em ficheiro
    with open("best_params.json", "w") as f:
        json.dump(best_params, f, indent=4)
    print("Hiperparâmetros salvos em 'best_params.json'.")

if __name__ == "__main__":
    run_optimization(n_trials=100)
