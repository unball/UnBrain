import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import pickle
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tools import motors2speeds_from_vl_vr

# --- Configurações Globais ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATASET_FILENAME = 'UnBrainDataSet_translated copy.csv'
MODEL_SAVE_PATH = "best_translator_model.pth"
SCALER_X_PATH = "scaler_x.pkl"
SCALER_Y_PATH = "scaler_y.pkl"

print(f"Usando dispositivo: {DEVICE}")

# --- Definição do Modelo ---
class CommandTranslatorNN(nn.Module):
    """
    Rede Neural que atua como um tradutor de comandos de velocidade,
    adaptando os comandos de um sistema de referência para um sistema alvo.
    A LSTM permite capturar a dinâmica (inércia, lag) do sistema.
    """
    def __init__(self, use_lstm=True):
        super().__init__()
        self.use_lstm = use_lstm
        
        self.fc1 = nn.Linear(4, 64)
        self.relu = nn.ReLU()
        
        if self.use_lstm:
            self.lstm = nn.LSTM(input_size=64, hidden_size=64, batch_first=True)
        
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)
        
    def forward(self, x, hidden=None):
        x = self.relu(self.fc1(x))
        if self.use_lstm:
            # A LSTM espera uma dimensão de sequência: (batch, seq_len, features)
            x, hidden = self.lstm(x.unsqueeze(1), hidden)
            x = x.squeeze(1)
        x = self.relu(self.fc2(x))
        output = self.fc3(x)
        return output, hidden

# --- Wrapper para Execução em Tempo Real ---
class SimToRealWrapper:
    """
    Encapsula o modelo treinado e os scalers para uso em tempo real.
    Recebe um comando de velocidade desejado (do sistema de referência)
    e retorna o comando adaptado para o sistema alvo (travesim).
    """
    def __init__(self, model_path, scaler_x_path, scaler_y_path, use_lstm=True):
        self.tradutor = CommandTranslatorNN(use_lstm=use_lstm).to(DEVICE)
        self.model = None
        self.model_path = model_path
        
        
        self.scaler_x_path = scaler_x_path
        self.scaler_y_path = scaler_y_path
        self.scaler_X = None
        self.scaler_y = None
        if self.scaler_X == None or self.scaler_y == None:
            with open(self.scaler_x_path, 'rb') as f:
                self.scaler_X = pickle.load(f)
            with open(self.scaler_y_path, 'rb') as f:
                self.scaler_y = pickle.load(f)

        self.prev_v_ref = 0.0
        self.prev_w_ref = 0.0
        self.hidden_state = None

    def step(self, v_desired, w_desired):
        """
        Recebe o comando de referência e retorna o comando atuado.
        """
        if self.model == None:
            self.model = self.tradutor
            self.model.load_state_dict(torch.load(self.model_path, map_location=DEVICE))
            self.model.eval()  # Fundamental: desativa tradutor como Dropout/BatchNorm
        # 1. Preparar e escalar a 

        input_data = np.array([[v_desired, w_desired, self.prev_v_ref, self.prev_w_ref]])
        input_scaled = self.scaler_X.transform(input_data)
        input_tensor = torch.FloatTensor(input_scaled).to(DEVICE)
        
        with torch.no_grad():
            # 2. Inferência do modelo
            output_scaled, self.hidden_state = self.model(input_tensor, self.hidden_state)
            
            # 3. Desfazer a escala da saída para obter o comando real
            actuated_cmd_scaled = output_scaled.cpu().numpy()
            actuated_cmd_unscaled = self.scaler_y.inverse_transform(actuated_cmd_scaled)
            v_actuated, w_actuated = actuated_cmd_unscaled[0]
        
        # 4. Atualizar estado para a próxima iteração
        self.prev_v_ref, self.prev_w_ref = v_desired, w_desired
        return v_actuated, w_actuated

# --- Coleta e Preparação de Dados ---
class DataCollector:
    """
    Coleta pares de (comando de referência, comando atuado) para criar o dataset.
    """
    def __init__(self, world, filename=DATASET_FILENAME):
        self.prev_v_ref = 0.0
        self.prev_w_ref = 0.0
        self.world = world
        self.filename = filename

        with open(self.filename, 'w') as f:
            f.write("v_ref,w_ref,prev_v_ref,prev_w_ref,v_act,w_act\n")

    def collect(self):
        if self.world.team[0].entity is not None:
            # Comando de REFERÊNCIA (o "desejo" da IA original)
            vl_ref, vr_ref = self.world.team[0].entity.control.actuateSimu(self.world.team[0])
            r_ref = 0.026
            L_ref = (0.0025 + 0.0375) * 2
            v_ref, w_ref = motors2speeds_from_vl_vr(vl_ref, vr_ref, r_ref, L_ref)
            
            # Comando ATUADO (a velocidade observada no travesim como resultado)
            v_actuated = self.world.team[0].v_signed
            w_actuated = self.world.team[0].w
            
            with open(self.filename, 'a') as f:
                f.write(f"{v_ref:.10f},{w_ref:.10f},"
                        f"{self.prev_v_ref:.10f},{self.prev_w_ref:.10f},"
                        f"{v_actuated:.10f},{w_actuated:.10f}\n")

            self.prev_v_ref, self.prev_w_ref = v_ref, w_ref

def load_and_preprocess_dataset(filename):
    """
    Carrega, pré-processa e divide o dataset para o treinamento.
    """
    df = pd.read_csv(filename)
    # Limpeza básica de dados
    df.dropna(inplace=True)
    
    # Entradas (features): comandos de referência
    X = df[['v_ref', 'w_ref', 'prev_v_ref', 'prev_w_ref']].values.astype(np.float32)
    # Saídas (alvos): comandos atuados/observados
    y = df[['v_act', 'w_act']].values.astype(np.float32)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

    # Padronização dos dados
    scaler_X = StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_val_scaled = scaler_X.transform(X_val)
    
    scaler_y = StandardScaler()
    y_train_scaled = scaler_y.fit_transform(y_train)
    y_val_scaled = scaler_y.transform(y_val)
    
    return X_train_scaled, y_train_scaled, X_val_scaled, y_val_scaled, scaler_X, scaler_y

# --- Função de Treinamento ---
def train_model(model, X_train, y_train, X_val, y_val, epochs=100, batch_size=128):
    train_dataset = torch.utils.data.TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_dataset = torch.utils.data.TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size)

    model = model.to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    best_val_loss = float('inf')
    epochs_no_improve = 0
    patience = 10  # Parar após 10 épocas sem melhora na validação

    print("\n--- Iniciando Treinamento ---")
    for epoch in range(epochs):
        model.train()
        total_train_loss = 0.0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
            optimizer.zero_grad()
            outputs, _ = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()

        model.eval()
        total_val_loss = 0.0
        with torch.no_grad():
            for batch_X_val, batch_y_val in val_loader:
                batch_X_val, batch_y_val = batch_X_val.to(DEVICE), batch_y_val.to(DEVICE)
                outputs, _ = model(batch_X_val)
                val_loss = criterion(outputs, batch_y_val)
                total_val_loss += val_loss.item()
        
        avg_train_loss = total_train_loss / len(train_loader)
        avg_val_loss = total_val_loss / len(val_loader)
        
        print(f"Época {epoch+1}/{epochs} -> Perda de Treino: {avg_train_loss:.6f}, Perda de Validação: {avg_val_loss:.6f}")

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Parada antecipada! A validação não melhorou por {patience} épocas.")
                break
    
    print(f"\nMelhor perda de validação alcançada: {best_val_loss:.6f}")


if __name__ == "__main__":
    # Etapa 1: Coleta de Dados (descomente para executar)
    # print("Iniciando coleta de dados...")
    # world_mock = ... # Aqui você precisaria de um objeto 'world' funcional
    # collector = DataCollector(world_mock, filename=DATASET_FILENAME)
    # for _ in range(10000): # Exemplo: coletar 10000 pontos
    #     collector.collect()
    # print("Coleta de dados concluída.")

    # Etapa 2: Carregar, pré-processar e treinar o modelo
    try:
        X_train, y_train, X_val, y_val, scaler_X, scaler_y = load_and_preprocess_dataset(DATASET_FILENAME)
        
        model_translator = CommandTranslatorNN(use_lstm=True)
        train_model(model_translator, X_train, y_train, X_val, y_val)
        
        # Etapa 3: Salvar os scalers para uso em produção
        with open(SCALER_X_PATH, 'wb') as f:
            pickle.dump(scaler_X, f)
        with open(SCALER_Y_PATH, 'wb') as f:
            pickle.dump(scaler_y, f)
        
        print(f"\nTreinamento concluído. Melhor modelo salvo como '{MODEL_SAVE_PATH}'.")
        print(f"Scalers salvos como '{SCALER_X_PATH}' e '{SCALER_Y_PATH}'.")
        
        # Etapa 4: Exemplo de como usar o wrapper em um loop de controle
        print("\n--- Testando o Wrapper do Tradutor ---")
        wrapper = SimToRealWrapper(
            model_path=MODEL_SAVE_PATH,
            scaler_x_path=SCALER_X_PATH,
            scaler_y_path=SCALER_Y_PATH,
            use_lstm=True
        )
        
        for _ in range(5):
            v_desired_from_AI = np.random.uniform(-1.5, 1.5)
            w_desired_from_AI = np.random.uniform(-10, 10)
            
            print(f"Comando da IA de alto nível: V={v_desired_from_AI:.2f}, w={w_desired_from_AI:.2f}")
            v_act, w_act = wrapper.step(v_desired_from_AI, w_desired_from_AI)
            print(f"Comando TRADUZIDO para o travesim: V={v_act:.2f}, w={w_act}\n")

    except FileNotFoundError:
        print(f"Erro: O arquivo de dataset '{DATASET_FILENAME}' não foi encontrado.")
        print("Certifique-se de executar a etapa de coleta de dados primeiro.")