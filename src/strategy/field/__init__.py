import numpy as np
from tools import angl, unit, norml, angError, filt, sat

class Field:
    def __init__(self, Pb):
        self.Pb = Pb

    def F(self, P):
        pass

    def dth(self, th2, th1, dt):
        if th1 is None or th2 is None: return 0
        return angError(th2, th1) / dt

    def phi(self, P: tuple, d=0.0001):
        """Calcula o ângulo \\(\\phi = \\frac{\\partial \\theta_d}{\\partial x} \\cos(\\theta) + \\frac{\\partial \\theta_d}{\\partial y} \\sin(\\theta)\\) usado para o controle"""
        P = np.array(P)
        dx = filt((self.F(P+[d,0,0])-self.F(P-[d,0,0]))/(2*d), 15)
        dy = filt((self.F(P+[0,d,0])-self.F(P-[0,d,0]))/(2*d), 15)
        return (dx*np.cos(P[2]) + dy*np.sin(P[2]))

    def gamma(self, dth, v, phi):
        return dth - v*phi