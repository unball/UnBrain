import sys
sys.path.append("src/")

from abc import ABC, abstractmethod
import numpy as np
from scipy.optimize import shgo, brute
from tools import unit, norml

class Area:
    def __init__(self):
        super().__init__()

    @abstractmethod
    def P(self, t: float):
        pass

    def nearestTo(self, P):
        # argmin_t |self.P(t) - P|
        P = np.array(P)[:2]
        optimizer = brute(lambda t: norml(self.P(t[0] % 1) - P), [(0,1)])
        return min(max(round(optimizer[0], 2), 0), 1)

    def dP(self, t, d=0.001):
        return (self.P((t+d) % 1) - self.P((t-d) % 1)) / (2*d)

    def normalTo(self, tn):
        dP = self.dP(tn)

        normal = np.array([dP[1], -dP[0]])

        return normal / norml(normal)

    def distanceTo(self, tn, P):
        P = np.array(P)[:2]
        Pn = self.P(tn)
        n = self.normalTo(tn)

        return norml(P-Pn) * np.sign(np.dot(P-Pn, n))