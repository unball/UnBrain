import numpy as np
from tools import angError

class KalmanFilter:
    def __init__(self):
        # Incerteza da medida do sensor (posição da visão)
        # R=0 faz o filtro confiar 100% na visão para posição, eliminando lag
        self.R = 0

        # Matriz de estados (descreve o modelo discreto x(k) = Ax(k-1)) - será atualizada com dt
        self.A = np.array([[1, 0.033, 0.033**2/2],[0, 1.0, 0.033],[0, 0, 1]])

        # Vetor de estados: [posição, velocidade, aceleração]
        self.x = np.array([[0.],[0.],[0]])

        # Matriz de covariância dos estados (incerteza inicial não nula para aceleração)
        self.P = np.diag((0.1,.3,0.5))

        # Matriz Q de incerteza do modelo (será atualizada dinamicamente com o dt)
        self.Q = np.zeros((3,3))

        # Matriz de sensores: um sensor que mede posição
        self.H = np.array([[1,0,0]])
        
    def _update_matrices(self, dt):
        # Proteção contra dt=0
        if dt <= 0.001: dt = 0.001
            
        self.A = np.matrix([
            [1.0, dt, (dt**2/2)],
            [0.0, 1.0, dt],
            [0.0, 0.0, 1.0]
        ])

        # Matriz Q de incerteza do modelo calibrada como "Agressiva" (igual ao antigo UnBrain)
        E = np.array([[dt, (dt**2/2), (dt**3/6)]])
        self.Q = 50 * np.matmul(E.transpose(), E)

    def setInitialPos(self, pos):
        self.x = np.array([[pos],[0.],[0]])

    def predict(self, dt):
        self._update_matrices(dt)
        # Predição do modelo com base no estado atual
        xp = np.matmul(self.A,self.x)

        # Predição da matriz de covariância dos estados
        Pp = np.matmul(self.A, np.matmul(self.P,self.A.transpose())) + self.Q

        S = np.matmul(self.H, np.matmul(Pp,self.H.transpose())) + self.R

        # Matriz de ganhos
        K = np.matmul(np.matmul(Pp, self.H.transpose()), np.linalg.inv(S))

        return xp, K, Pp

    def estimate(self, z, dt):
        xp, K, Pp = self.predict(dt)

        # Calcula o resíduo (inovação)
        y = z - np.matmul(self.H, xp)
        
        self.x = xp + np.matmul(K, y)

        # Atualização da Covariância no Formato de Joseph (Matematicamente Estável)
        # P = (I - K*H) * Pp * (I - K*H)^T + K * R * K^T
        I = np.eye(3)
        I_KH = I - np.matmul(K, self.H)
        joseph_noise = self.R * np.matmul(K, K.transpose())
        self.P = np.matmul(I_KH, np.matmul(Pp, I_KH.transpose())) + joseph_noise

        # Forçador de Simetria para evitar corrupção por arredondamento de float64 do Python
        self.P = (self.P + self.P.transpose()) / 2.0
        
        # Trava de Segurança 2: Divergência da Covariância
        # Se a incerteza explodir (Traço > 1000) ou a velocidade explodir, o filtro divergiu. Reiniciamos covariância e dinâmicas.
        if np.trace(self.P) > 1000 or np.any(np.abs(self.x[1:]) > 1e4):
            self.P = np.diag((0.1, 0.3, 0.5))
            self.x[1] = 0.0
            self.x[2] = 0.0

        return self.x

    def predictOnly(self, dt):
        xp, K, Pp = self.predict(dt)
        
        self.x = xp
        self.P = Pp
        
        # Forçador de Simetria para evitar corrupção por arredondamento de float64 do Python
        self.P = (self.P + self.P.transpose()) / 2.0
        
        # Trava de Segurança 2: Divergência da Covariância
        # Se a incerteza explodir (Traço > 1000) ou a velocidade explodir, o filtro divergiu. Reiniciamos covariância e dinâmicas.
        if np.trace(self.P) > 1000 or np.any(np.abs(self.x[1:]) > 1e4):
            self.P = np.diag((0.1, 0.3, 0.5))
            self.x[1] = 0.0
            self.x[2] = 0.0
        
        return self.x

class KalmanFilterAngular(KalmanFilter):
    def __init__(self):
        super().__init__()
        # R = 0.5
        self.R = 0
    def _update_matrices(self, dt):
        # Proteção contra dt=0
        if dt <= 0.001: dt = 0.001
            
        self.A = np.matrix([
            [1.0, dt, (dt**2/2)],
            [0.0, 1.0, dt],
            [0.0, 0.0, 1.0]
        ])

        # Q = 100 para dar ao robô agilidade suficiente para acompanhar a velocidade da curva
        E = np.array([[dt, (dt**2/2), (dt**3/6)]])
        self.Q = 50 * np.matmul(E.transpose(), E)