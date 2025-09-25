import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import pickle
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tools import motors2speeds_from_vl_vr, speeds2motors

# --- Configurações Globais ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATASET_FILENAME = 'UnBrainDataSet_neuro.csv'
MODEL_SAVE_PATH = "neuro_controller_firasim.pth"
SCALER_X_PATH = "scaler_x_neuro_firasim.pkl"
SCALER_Y_PATH = "scaler_y_neuro_firasim.pkl"

RSIM_WHEEL_RADIUS = 0.026
RSIM_WHEEL_BASE_LENGTH = 0.08  # L

print(f"Usando dispositivo: {DEVICE}")

class PIDController:
    """ Controlador PID simples para gerar dados de treino de alta qualidade. """
    def __init__(self, Kp, Ki, Kd, output_limits=(-2.0, 2.0)):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.min_output, self.max_output = output_limits
        self.last_error, self.integral_sum = 0.0, 0.0
        self.last_time = time.time()
        self.setpoint = 0.0

    def update(self, measured_value):
        current_time = time.time()
        delta_time = current_time - self.last_time
        if delta_time == 0: delta_time = 1e-6
        error = self.setpoint - measured_value
        self.integral_sum += error * delta_time
        self.integral_sum = max(min(self.integral_sum, self.max_output), self.min_output)
        derivative_error = (error - self.last_error) / delta_time
        output = (self.Kp * error) + (self.Ki * self.integral_sum) + (self.Kd * derivative_error)
        self.last_error = error
        self.last_time = current_time
        return max(min(output, self.max_output), self.min_output)

class NeuroControllerNN(nn.Module):
    """
    Rede Neural que atua como um controlador adaptativo.
    Aprende a política de controle (como reagir aos erros) diretamente dos dados.
    """
    def __init__(self, input_size=8):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.relu1 = nn.ReLU()
        self.lstm = nn.LSTM(input_size=128, hidden_size=128, batch_first=True)
        self.fc2 = nn.Linear(128, 64)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(64, 2)

    def forward(self, x, hidden=None):
        x = self.bn1(self.fc1(x))
        x = self.relu1(x)
        x, hidden = self.lstm(x.unsqueeze(1), hidden)
        x = x.squeeze(1)
        x = self.relu2(self.fc2(x))
        return self.fc3(x), hidden



# --- Wrapper para Execução em Tempo Real ---
class NeuroControllerWrapper:
    """
    Encapsula o Neuro-Controlador e gerencia o estado (erros, etc.) em tempo real.
    """
    def __init__(self, model_path, scaler_x_path, scaler_y_path):
        self.model = NeuroControllerNN(input_size=8).to(DEVICE)
        self.model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        self.model.eval()

        with open(scaler_x_path, 'rb') as f: self.scaler_X = pickle.load(f)
        with open(scaler_y_path, 'rb') as f: self.scaler_y = pickle.load(f)

        self.last_error_v, self.last_error_w = 0.0, 0.0
        self.hidden_state = None
        self.last_time = time.time()

    def step(self, v_target, w_target, v_measured, w_measured):
        current_time = time.time()
        delta_time = current_time - self.last_time
        if delta_time == 0: delta_time = 1e-6

        error_v = v_target - v_measured
        error_w = w_target - w_measured
        
        derivative_error_v = (error_v - self.last_error_v) / delta_time
        derivative_error_w = (error_w - self.last_error_w) / delta_time

        input_data = np.array([[
            v_target, w_target, v_measured, w_measured,
            error_v, error_w, derivative_error_v, derivative_error_w
        ]])

        input_scaled = self.scaler_X.transform(input_data)
        input_tensor = torch.FloatTensor(input_scaled).to(DEVICE)

        with torch.no_grad():
            output_scaled, self.hidden_state = self.model(input_tensor, self.hidden_state)
            command_unscaled = self.scaler_y.inverse_transform(output_scaled.cpu().numpy())
            v_command, w_command = command_unscaled[0]

        self.last_error_v, self.last_error_w = error_v, error_w
        self.last_time = current_time
        return v_command, w_command

    
# --- Coleta e Preparação de Dados ---
class DataCollector:
    """
    Coleta dados de estado e comando para treinar o Neuro-Controlador.
    USA UM PID SIMPLES PARA GERAR DADOS DE TREINO "BONS".
    A IA aprenderá a imitar e superar este PID.
    """
    def __init__(self, world, filename=DATASET_FILENAME):
        self.world = world
        self.filename = filename
        self.pid_v = PIDController(Kp=2.5, Ki=0.1, Kd=0.05)
        self.pid_w = PIDController(Kp=1.8, Ki=0.08, Kd=0.03)
        self.last_error_v, self.last_error_w = 0.0, 0.0
        self.last_time = time.time()
        self.derivative_damping = 0.5 

        with open(self.filename, 'w') as f:
            f.write("v_target,w_target,v_measured,w_measured,"
                    "error_v,error_w,derivative_error_v,derivative_error_w,"
                    "v_command,w_command\n")

    def collect_and_actuate(self, v_target, w_target):
        current_time = time.time()
        if (delta_time := current_time - self.last_time) < 1e-4: delta_time = 1e-4
        
        # Estas linhas dependem do seu ambiente de simulação.
        # Substitua por valores reais do seu 'world'
        v_measured = self.world.team[0].v_signed 
        w_measured = self.world.team[0].w
        
        # CORREÇÃO 2: O setpoint do PID precisa ser atualizado a cada passo!
        self.pid_v.setpoint = v_target
        self.pid_w.setpoint = w_target
        v_command = self.pid_v.update(v_measured)
        w_command = self.pid_w.update(w_measured)
        
        error_v = v_target - v_measured
        error_w = w_target - w_measured
        
        current_derivative_v = (error_v - self.last_error_v) / delta_time
        current_derivative_w = (error_w - self.last_error_w) / delta_time
        
        if not hasattr(self, 'last_derivative_v'):
            self.last_derivative_v, self.last_derivative_w = current_derivative_v, current_derivative_w

        stable_derivative_v = self.derivative_damping * self.last_derivative_v + (1 - self.derivative_damping) * current_derivative_v
        stable_derivative_w = self.derivative_damping * self.last_derivative_w + (1 - self.derivative_damping) * current_derivative_w
        
        with open(self.filename, 'a') as f:
            f.write(f"{v_target:.6f},{w_target:.6f},"
                    f"{v_measured:.6f},{w_measured:.6f},"
                    f"{error_v:.6f},{error_w:.6f},"
                    f"{stable_derivative_v:.6f},{stable_derivative_w:.6f},"
                    f"{v_command:.6f},{w_command:.6f}\n")
        
        self.last_error_v, self.last_error_w = error_v, error_w
        self.last_time = current_time
        self.last_derivative_v, self.last_derivative_w = stable_derivative_v, stable_derivative_w
        return v_command, w_command


def clean_neuro_dataset(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """ Limpeza adaptada para o dataset do Neuro-Controlador. """
    initial_rows = len(df)
    if verbose: print(f"--- Limpeza Autônoma do Dataset ---\nNúmero de amostras inicial: {initial_rows}")
    
    # CORREÇÃO 3: Remover outliers com base na derivada, que é a fonte de instabilidade
    # Remove qualquer linha onde a derivada seja absurdamente alta (fisicamente impossível)
    max_reasonable_derivative = 1000 
    cleaned_df = df[np.abs(df['derivative_error_v']) < max_reasonable_derivative]
    cleaned_df = cleaned_df[np.abs(cleaned_df['derivative_error_w']) < max_reasonable_derivative]
    
    removed_count = initial_rows - len(cleaned_df)
    if verbose: print(f"Removidas {removed_count} amostras com derivada instável.")
    return cleaned_df

def load_and_preprocess_neuro_dataset(filename):
    """ Carrega e prepara o dataset para o Neuro-Controlador. """
    df = pd.read_csv(filename)
    df = clean_neuro_dataset(df) # Limpeza opcional, mas recomendada
    df.dropna(inplace=True)

    X = df[['v_target', 'w_target', 'v_measured', 'w_measured', 
            'error_v', 'error_w', 'derivative_error_v', 'derivative_error_w']].values.astype(np.float32)
    y = df[['v_command', 'w_command']].values.astype(np.float32)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler_X = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(y_train)
    
    return scaler_X.transform(X_train), scaler_y.transform(y_train), \
           scaler_X.transform(X_val), scaler_y.transform(y_val), \
           scaler_X, scaler_y


# --- Função de Treinamento ---
def train_model(model, X_train, y_train, X_val, y_val, epochs=100, batch_size=256):
    train_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(
        torch.FloatTensor(X_train), torch.FloatTensor(y_train)), batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(
        torch.FloatTensor(X_val), torch.FloatTensor(y_val)), batch_size=batch_size)

    model = model.to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.2, verbose=True)
    criterion = nn.MSELoss()
    best_val_loss = float('inf')

    print("\n--- Iniciando Treinamento do Neuro-Controlador ---")
    for epoch in range(epochs):
        model.train()
        # ... (laço de treino) ...
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch_X_val, batch_y_val in val_loader:
                outputs, _ = model(batch_X_val.to(DEVICE))
                total_val_loss += criterion(outputs, batch_y_val.to(DEVICE)).item()
        avg_val_loss = total_val_loss / len(val_loader)
        scheduler.step(avg_val_loss)
        print(f"Época {epoch+1}/{epochs} -> Perda de Validação: {avg_val_loss:.6f}")
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Melhor perda de validação: {best_val_loss:.6f}")


if __name__ == "__main__":
    try:
        X_train, y_train, X_val, y_val, scaler_X, scaler_y = load_and_preprocess_neuro_dataset(DATASET_FILENAME)
        
        neuro_controller_model = NeuroControllerNN(input_size=X_train.shape[1])
        train_model(neuro_controller_model, X_train, y_train, X_val, y_val)
        
        with open(SCALER_X_PATH, 'wb') as f: pickle.dump(scaler_X, f)
        with open(SCALER_Y_PATH, 'wb') as f: pickle.dump(scaler_y, f)
        
        print(f"\nTreinamento concluído. Modelo salvo em '{MODEL_SAVE_PATH}'.")

        print("\n--- Testando o Wrapper do Neuro-Controlador ---")
        wrapper = NeuroControllerWrapper(MODEL_SAVE_PATH, SCALER_X_PATH, SCALER_Y_PATH)
        
        v_target, w_target = 1.2, -8.0
        v_measured, w_measured = 0.0, 0.0

        for i in range(20):
            print(f"\nPasso {i+1}: Alvo(V={v_target:.2f}, W={w_target:.2f}), Medido(V={v_measured:.2f}, W={w_measured:.2f})")
            v_cmd, w_cmd = wrapper.step(v_target, w_target, v_measured, w_measured)
            print(f"==> Comando Gerado: V={v_cmd:.2f}, W={w_cmd:.2f}")
            v_measured += (v_target - v_measured) * np.random.uniform(0.3, 0.5)
            w_measured += (w_target - w_measured) * np.random.uniform(0.3, 0.5)

    except FileNotFoundError:
        print(f"\nERRO: O arquivo de dataset '{DATASET_FILENAME}' não foi encontrado.")
        print("Isto é esperado se for a primeira execução.")
        print("Certifique-se de que a etapa de COLETA DE DADOS está implementada no seu código de simulação para gerar este arquivo.")