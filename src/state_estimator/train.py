import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import argparse
import os

import json
from neural_estimator import NeuralStateEstimator
from tune import ensure_hpo_dataset

def train_model(dataset_path=None, epochs=20, default_batch_size=128, fine_tune_path=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Treinando em: {device}")
    
    # 1. Carregar Hiperparâmetros Otimizados
    history_size = 10
    hidden_dim = 64
    lr = 1e-3
    batch_size = default_batch_size
    
    if os.path.exists("best_params.json"):
        with open("best_params.json", "r") as f:
            best_params = json.load(f)
        history_size = best_params.get("history_size", history_size)
        hidden_dim = best_params.get("hidden_dim", hidden_dim)
        lr = best_params.get("learning_rate", lr)
        batch_size = best_params.get("batch_size", batch_size)
        print(f"Lendo best_params.json -> LR: {lr:.5f}, Batch: {batch_size}, History: {history_size}, Hidden: {hidden_dim}")
    else:
        print("Aviso: best_params.json não encontrado. Usando defaults.")

    # 2. Carregar e fatiar o dataset adequadamente
    if not dataset_path:
        if os.path.exists("data/sim2real_dataset.pt"):
            dataset_path = "data/sim2real_dataset.pt"
        else:
            # Se não existir um dataset genérico, recorremos ao HPO dataset builder
            max_history = max(15, history_size)
            dataset_path = ensure_hpo_dataset(max_history=max_history)
        
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset não encontrado: {dataset_path}. Rode generate_dataset.py primeiro.")
        
    data = torch.load(dataset_path, map_location="cpu", weights_only=False)
    
    # Validações de Metadados
    if "metadata" in data:
        meta = data["metadata"]
        if meta["history_size"] != history_size:
            print(f"AVISO: O dataset foi gerado com history_size={meta['history_size']}, mas o train.py está configurado para {history_size}.")
            assert history_size <= meta["history_size"], "history_size do treino não pode ser maior que o do dataset!"
    
    # Fazemos slice da janela de histórico, caso tenhamos reduzido o history_size no best_params
    X_train_tensor = data["X_train"][:, -history_size:, :]
    Y_train_tensor = data["Y_train"]
    X_val_tensor = data["X_val"][:, -history_size:, :]
    Y_val_tensor = data["Y_val"]
    
    train_dataset = TensorDataset(X_train_tensor, Y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, Y_val_tensor)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Instanciar Modelo com os parâmetros da arquitetura dinâmicos
    model = NeuralStateEstimator(history_size=history_size, hidden_dim=hidden_dim).to(device)
    
    if fine_tune_path:
        print(f"Carregando pesos de {fine_tune_path} para FINE-TUNING...")
        state_dict = torch.load(fine_tune_path, map_location=device)
        model.load_state_dict(state_dict)
        lr = 1e-5
        epochs = max(5, epochs // 2)

    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    
    # Robustez contra outliers físicos (colisões bruscas da simulação)
    # Huber Loss (SmoothL1) reduz o gradiente para erros altos
    criterion = nn.SmoothL1Loss(beta=0.1)
    
    best_val_loss = float('inf')
    
    print(f"Iniciando treinamento ({epochs} epochs)...")
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            preds = model(batch_x)
            
            # O target também precisa ser normalizado internamente?
            # Não, a saída do modelo denormalize_output(pred_norm) já retorna na escala real!
            # Então podemos medir a loss diretamente no domínio físico.
            loss = criterion(preds, batch_y)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * batch_x.size(0)
            
        train_loss /= len(train_dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                preds = model(batch_x)
                loss = criterion(preds, batch_y)
                val_loss += loss.item() * batch_x.size(0)
        val_loss /= len(val_dataset)
        
        print(f"Epoch {epoch+1:02d}/{epochs} | Train Loss: {train_loss:.5f} | Val Loss: {val_loss:.5f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Salvar state_dict para fine-tuning
            torch.save(model.state_dict(), "best_sim2real_model.pth")
            # Salvar compilado para inferência O(1) na CPU embarcada
            jit_model = torch.jit.script(model)
            jit_model = torch.jit.optimize_for_inference(jit_model)
            jit_model.save("neural_estimator_jit.pth")
            
    print("Treinamento concluído. Modelo JIT salvo em 'neural_estimator_jit.pth'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--fine-tune", type=str, default="", help="Caminho do .pth pré-treinado")
    args = parser.parse_args()
    
    train_model(
        epochs=args.epochs,
        default_batch_size=args.batch_size,
        fine_tune_path=args.fine_tune if args.fine_tune else None
    )
