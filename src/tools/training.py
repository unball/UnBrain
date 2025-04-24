import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import time
from tools import speeds2motors

class LowLevelController(nn.Module):
    def __init__(self, use_lstm=False):
        super().__init__()
        self.use_lstm = use_lstm
        
        # Camada inicial comum
        self.fc1 = nn.Linear(4, 64)
        self.relu = nn.ReLU()
        
        # Componente temporal (NAS)
        if use_lstm:
            self.lstm = nn.LSTM(64, 64, batch_first=True)
        
        # Camadas finais (VSSS-RL)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)
        
        # Estado temporal
        self.hidden = None

    def forward(self, x, hidden=None):
        x = self.relu(self.fc1(x))
        
        if self.use_lstm:
            # Processamento temporal (NAS)
            x, self.hidden = self.lstm(x.unsqueeze(0), hidden)
            x = x.squeeze(0)
        
        x = self.relu(self.fc2(x))
        return self.fc3(x), self.hidden
    
class SimToRealWrapper:
    def __init__(self, model_path, use_lstm=False):
        self.model = LowLevelController(use_lstm=use_lstm)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # Estado temporal
        self.prev_vl = 0.0
        self.prev_vr = 0.0
        self.hidden = None

    def step(self, v_desired, omega_desired):
        input_tensor = torch.FloatTensor([[
            v_desired,
            omega_desired,
            self.prev_vl,
            self.prev_vr
        ]])
        
        with torch.no_grad():
            output, self.hidden = self.model(input_tensor, self.hidden)
            vl, vr = output[0].numpy()
        
        # Atualizar estado
        self.prev_vl, self.prev_vr = vl, vr
        return vl, vr

# Função para coletar dados de treino da simulação
class DataCollector:
    def __init__(self, world, filename = 'UnBrainDataSet.csv',steps_per_episode=60, num_episodes=60*4):
        self.steps = steps_per_episode
        self.tempo = 0
        self.prev_vl = 0.0
        self.prev_vr = 0.0
        self.episodes = 0
        self.contagem = 0
        self.num_episodes = num_episodes
        self.world = world
        self.filename = filename

        with open(self.filename, 'w') as f:
            f.write("vr_unbrain,vl_unbrain,prev_vl,prev_vr,vl_real,vr_real\n")

    def collect(self):
        if time.time() - self.tempo > 1/self.steps and self.episodes < self.num_episodes and self.world.team[0].entity is not None:          
            # for _ in range(self.num_episodes):
                
            #     for _ in range(100):  # 100 steps por episódio
                    # Obter ação desejada da política de alto nível (exemplo)
            v_desired = self.world.team[0].v_signed
            omega_desired = self.world.team[0].w

            vr_unbrain, vl_unbrain = speeds2motors(v_desired, omega_desired)
            
            # Obter velocidades reais das rodas (simulado)
            vl_real, vr_real = self.world.team[0].entity.control.actuateSimu(self.world.team[0])
            
            # Armazenar dados
            with open(self.filename, 'a') as f:
                f.write(f"{vr_unbrain + np.random.normal(0, 0.1):.10f},{vl_unbrain + np.random.normal(0, 0.1):.10f},{self.prev_vl:.10f},{self.prev_vr:.10f},{vl_real:.10f},{vr_real:.10f}\n")

            self.tempo = time.time()
            # Atualizar velocidades anteriores
            self.prev_vl, self.prev_vr = vl_real, vr_real
            self.contagem +=1
            
            if self.contagem == 60:
                self.episodes +=1
                self.contagem = 0

        elif self.episodes > self.num_episodes:
            print("Fim da coleetagem de dados")
    
def load_dataset(filename):
    # Carregar dados do arquivo
    data = np.loadtxt(filename, delimiter=',', skiprows=1)  # Pular cabeçalho
    
    # Separar inputs e targets
    X = data[:, :4].astype(np.float32)  # Primeiras 4 colunas
    y = data[:, 4:].astype(np.float32)  # Últimas 2 colunas
    
    return X, y

def train_model(model, X, y, epochs=50, batch_size=64):
    
    dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(X),
        torch.FloatTensor(y)
    )
    
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.MSELoss()
    
    for epoch in range(epochs):
        total_loss = 0.0
        hidden = None
        
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            
            # Resetar estado LSTM a cada batch (NAS)
            if model.use_lstm:
                hidden = None
                
            outputs, _ = model(batch_X, hidden)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}/{epochs} Loss: {total_loss/len(loader):.4f}")

if __name__ == "__main__":
    
    # Treinar modelo com LSTM (NAS)
    model = LowLevelController(use_lstm=True)
    X, y = load_dataset('UnBrainDataSet.csv')
    train_model(model, X, y)
    
    # Salvar modelo
    torch.save(model.state_dict(), "sim2real_model.pth")
    
    # Usar wrapper (VSSS-RL)
    wrapper = SimToRealWrapper("sim2real_model.pth", use_lstm=True)
    
    # # Exemplo de controle em tempo real
    # for _ in range(100):
    #     v_desired = 0.5  # Exemplo de política de alto nível
    #     omega_desired = 1.0
    #     vl, vr = wrapper.step(v_desired, omega_desired)
    #     print(f"Comando: VL={vl:.2f}, VR={vr:.2f}")
