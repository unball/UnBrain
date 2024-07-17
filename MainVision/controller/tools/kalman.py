import numpy as np

class KalmanFilter:
    def __init__(self):
        # Período
        T = 0.033

        # Incerteza da medida do sensor (posição da visão) +-5cm
        self.R = 0

        # Matriz de estados (descreve o modelo discreto x(k) = Ax(k-1))
        self.A = np.array([[1, T, T**2/2],[0, 1.0, T],[0, 0, 1]])

        # Vetor de estados: [posição, velocidade, aceleração]
        self.x = np.array([[0.],[0.],[0]])

        # Matriz de covariância dos estados (incerteza inicial não nula para aceleração)
        self.P = np.diag((0.1,.3,0.5))

        # Matriz Q de incerteza do modelo
        E = np.array([[T, (T**2/2), (T**3/6)]])
        self.Q = 1000*np.matmul(E.transpose(),E)

        # Matriz de sensores: um sensor que mede posição
        self.H = np.array([[1,0,0]])

    def setInitialPos(self, pos):
        self.x = np.array([[pos],[0.],[0]])

    def predict(self):
        # Predição do modelo com base no estado atual
        xp = np.matmul(self.A,self.x)

        # Predição da matriz de covariância dos estados
        Pp = np.matmul(self.A, np.matmul(self.P,self.A.transpose())) + self.Q

        S = np.matmul(self.H, np.matmul(Pp,self.H.transpose())) + self.R

        # Matriz de ganhos
        K = np.matmul(np.matmul(Pp, self.H.transpose()), np.linalg.inv(S))

        return xp, K, Pp

    def estimate(self, z):
        xp, K, Pp = self.predict()

        self.x = xp + np.matmul(K, z - np.matmul(self.H, xp))
        self.P = np.matmul((np.eye(3)-np.matmul(K,self.H)), Pp)

        return self.x