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
DATASET_FILENAME = 'UnBrainDataSet_translated.csv'
MODEL_SAVE_PATH = "best_model_firasim.pth"
SCALER_X_PATH = "scaler_x_firasim.pkl"
SCALER_Y_PATH = "scaler_y_firasim.pkl"

RSIM_WHEEL_RADIUS = 0.026
RSIM_WHEEL_BASE_LENGTH = 0.08  # L

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
            x, hidden = self.lstm(x.unsqueeze(1), hidden)
            x = x.squeeze(1)
        x = self.relu(self.fc2(x))
        output = self.fc3(x)
        return output, hidden

# --- Wrapper para Execução em Tempo Real ---
class SimToRealWrapper:
    """
    Encapsula o modelo e os scalers. Carrega todos os recursos na inicialização.
    """
    def __init__(self, model_path, scaler_x_path, scaler_y_path, use_lstm=True):
        # 1. Carregar o modelo treinado UMA VEZ.
        self.model = CommandTranslatorNN(use_lstm=use_lstm).to(DEVICE)
        self.model.load_state_dict(torch.load(model_path, map_location=DEVICE, weights_only=True))
        self.model.eval()  # Fundamental: desativa camadas como Dropout/BatchNorm

        # 2. Carregar os scalers UMA VEZ.
        with open(scaler_x_path, 'rb') as f:
            self.scaler_X = pickle.load(f)
        with open(scaler_y_path, 'rb') as f:
            self.scaler_y = pickle.load(f)

        # 3. Inicializar o estado.
        self.prev_v_ref = 0.0
        self.prev_w_ref = 0.0
        self.hidden_state = None

    def step(self, v_desired, w_desired):
        """
        Recebe o comando de referência e retorna o comando atuado.
        """
        # Preparar e escalar a entrada
        input_data = np.array([[v_desired, w_desired, self.prev_v_ref, self.prev_w_ref]])
        input_scaled = self.scaler_X.transform(input_data)
        input_tensor = torch.FloatTensor(input_scaled).to(DEVICE)
        
        with torch.no_grad():
            # Inferência do modelo
            output_scaled, self.hidden_state = self.model(input_tensor, self.hidden_state)
            
            # Desfazer a escala da saída
            actuated_cmd_scaled = output_scaled.cpu().numpy()
            actuated_cmd_unscaled = self.scaler_y.inverse_transform(actuated_cmd_scaled)
            v_actuated, w_actuated = actuated_cmd_unscaled[0]
        
        # Atualizar estado para a próxima iteração
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

    def collect(self, vl_AI, vr_AI):
        if self.world.team[0].entity is not None:
            # # Comando de REFERÊNCIA (o "desejo" da IA original, interpretado com parâmetros do rSim)
            # vl_ref, vr_ref = self.world.team[0].entity.control.actuateSimu(self.world.team[0])
            # Usa os parâmetros corretos e explícitos do rSim
            v_ref, w_ref = motors2speeds_from_vl_vr(vl_AI, vr_AI, RSIM_WHEEL_RADIUS, RSIM_WHEEL_BASE_LENGTH)
            
            # Comando ATUADO (a velocidade observada no travesim como resultado)
            v_actuated_raw = self.world.team[0].v_signed
            w_actuated = self.world.team[0].w

            v_actuated_corrected = np.copysign(np.abs(v_actuated_raw), v_ref)

            # Se v_ref for muito próximo de zero, v_actuated também deve ser.
            if np.abs(v_ref) < 0.01:
                v_actuated_corrected = 0.0
                
            with open(self.filename, 'a') as f:
                f.write(f"{v_ref:.10f},{w_ref:.10f},"
                        f"{self.prev_v_ref:.10f},{self.prev_w_ref:.10f},"
                        # Salva a velocidade linear corrigida
                        f"{v_actuated_corrected + np.random.normal(0, 0.1/2):.10f},{w_actuated + np.random.normal(0, 0.1/2):.10f}\n")
                        # f"{v_actuated_corrected + np.random.normal(0, 0.1/2):.10f},{w_actuated + np.random.normal(0, 0.1/2):.10f}\n")

            self.prev_v_ref, self.prev_w_ref = v_ref, w_ref

def clean_robot_dataset(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Realiza uma limpeza autônoma em um dataset de controle de robô.

    Args:
        df (pd.DataFrame): O DataFrame original carregado do CSV.
        verbose (bool): Se True, imprime o número de linhas removidas em cada etapa.

    Returns:
        pd.DataFrame: O DataFrame limpo e pronto para o treinamento.
    """
    initial_rows = len(df)
    if verbose:
        print(f"--- Iniciando Limpeza Autônoma do Dataset ---")
        print(f"Número de amostras inicial: {initial_rows}")

    # Cópia para evitar modificar o DataFrame original fora da função
    cleaned_df = df.copy()

    # --- Regra 1: Remover Inconsistências de Sinal ---
    # Causa mais provável da instabilidade. Remove linhas onde o robô virou para
    # o lado oposto ao comandado, o que é fisicamente anômalo (exceto perto de zero).
    # Usamos uma pequena tolerância (threshold) para não penalizar pequenas flutuações.
    sign_tolerance = 0.01
    
    # Condição para inconsistência em 'v'
    v_sign_inconsistent = (np.sign(cleaned_df['v_ref']) != np.sign(cleaned_df['v_act'])) & \
                          (np.abs(cleaned_df['v_ref']) > sign_tolerance) & \
                          (np.abs(cleaned_df['v_act']) > sign_tolerance)
                          
    # Condição para inconsistência em 'w'
    w_sign_inconsistent = (np.sign(cleaned_df['w_ref']) != np.sign(cleaned_df['w_act'])) & \
                          (np.abs(cleaned_df['w_ref']) > sign_tolerance) & \
                          (np.abs(cleaned_df['w_act']) > sign_tolerance)

    # Remove as linhas que satisfazem qualquer uma das condições de inconsistência
    inconsistent_rows = cleaned_df[v_sign_inconsistent | w_sign_inconsistent]
    cleaned_df = cleaned_df.drop(inconsistent_rows.index)
    
    if verbose:
        print(f"Etapa 1 (Inconsistência de Sinal): Removidas {len(inconsistent_rows)} amostras.")

    # --- Regra 2: Remover Outliers Extremos (Z-score) ---
    # Remove anomalias causadas por colisões ou falhas de sensor, onde a diferença
    # entre o comando e o resultado é estatisticamente improvável.
    
    # Calcula o erro absoluto entre referência e real
    cleaned_df['v_error'] = np.abs(cleaned_df['v_ref'] - cleaned_df['v_act'])
    cleaned_df['w_error'] = np.abs(cleaned_df['w_ref'] - cleaned_df['w_act'])
    
    # Calcula o Z-score para os erros
    cleaned_df['v_error_zscore'] = np.abs((cleaned_df['v_error'] - cleaned_df['v_error'].mean()) / cleaned_df['v_error'].std())
    cleaned_df['w_error_zscore'] = np.abs((cleaned_df['w_error'] - cleaned_df['w_error'].mean()) / cleaned_df['w_error'].std())
    
    # Define um limiar de Z-score (3 é um valor comum, significando 3 desvios padrão)
    z_score_threshold = 3.0
    
    # Identifica os outliers
    outlier_rows = cleaned_df[(cleaned_df['v_error_zscore'] > z_score_threshold) | 
                              (cleaned_df['w_error_zscore'] > z_score_threshold)]
    cleaned_df = cleaned_df.drop(outlier_rows.index)
    
    if verbose:
        print(f"Etapa 2 (Remoção de Outliers): Removidas {len(outlier_rows)} amostras.")

    # Limpa as colunas auxiliares que foram criadas
    cleaned_df = cleaned_df.drop(columns=['v_error', 'w_error', 'v_error_zscore', 'w_error_zscore'])

    final_rows = len(cleaned_df)
    removed_count = initial_rows - final_rows
    removed_percent = (removed_count / initial_rows) * 100
    
    if verbose:
        print(f"\nLimpeza Concluída.")
        print(f"Total de amostras removidas: {removed_count} ({removed_percent:.2f}%)")
        print(f"Número de amostras final: {final_rows}")
        print("---------------------------------------------")
        
    return cleaned_df

def load_and_preprocess_dataset(filename):
    """
    Carrega, pré-processa e divide o dataset para o treinamento.
    """
    df = pd.read_csv(filename)

    df = clean_robot_dataset(df)

    df.dropna(inplace=True)

    # Entradas (features): A velocidade que queremos ATINGIR no final.
    # Usamos as colunas '_act' do dataset como nosso "alvo desejado".
    X = df[['v_act', 'w_act']].values.astype(np.float32)
    
    # Saídas (alvos): O comando que precisamos ENVIAR para atingir o alvo.
    # Usamos as colunas '_ref' como o comando que a rede deve aprender a gerar.
    y = df[['v_ref', 'w_ref']].values.astype(np.float32)

    # Para manter a memória de estado, precisamos adicionar as velocidades anteriores
    # à entrada. A entrada agora será [v_alvo, w_alvo, v_comando_anterior, w_comando_anterior]
    prev_refs = df[['prev_v_ref', 'prev_w_ref']].values.astype(np.float32)
    X = np.concatenate([X, prev_refs], axis=1)

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
def train_model(model, X_train, y_train, X_val, y_val, epochs=250, batch_size=128):
    train_dataset = torch.utils.data.TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_dataset = torch.utils.data.TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size)

    model = model.to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.1)
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

        scheduler.step(avg_val_loss)
        
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
        X_train, y_train, X_val, y_val, scaler_X, scaler_y = load_and_preprocess_dataset("UnBrainDataSet_translated copy.csv")
        
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
        
        for _ in range(20):
            v_desired_from_AI = np.random.uniform(-1.5, 1.5)
            w_desired_from_AI = np.random.uniform(-10, 10)
            
            print(f"Comando da IA de alto nível: V={v_desired_from_AI:.2f}, w={w_desired_from_AI:.2f}")
            v_act, w_act = wrapper.step(v_desired_from_AI, w_desired_from_AI)
            print(f"Comando TRADUZIDO para o travesim: V={v_act:.2f}, w={w_act}\n")

    except FileNotFoundError:
        print(f"Erro: O arquivo de dataset '{DATASET_FILENAME}' não foi encontrado.")
        print("Certifique-se de executar a etapa de coleta de dados primeiro.")