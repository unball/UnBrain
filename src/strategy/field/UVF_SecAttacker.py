
import numpy as np
from tools import angl, unit, norml, angError, filt, sat
from . import Field

class UVF(Field):
    def __init__(self, Pb, radius=0.13, direction=0, spiral=True, Kr=0.03, Kr_single=0.03, nullgamma=False):
        super().__init__(Pb)

        # Raio da espiral
        self.r = radius

        # Direção da espiral, 0 para duas espirais
        self.direction = direction

        # Habilita espiral interna, caso contrário são retas 
        self.spiral = spiral

        # Constantes das espirais duplas
        self.Kr = Kr

        # Constante da espiral únicas
        self.Kr_single = Kr_single


    def F(self, P):
        return self.TUF(np.array(P), np.array(self.Pb))

    def TUF(self, P, Pb):
        
        P = P.copy()

        # Ajusta o sistema de coordenadas
        P[:2] = P[:2]-Pb[:2]
        rotMatrix = np.array([[np.cos(Pb[2]), np.sin(Pb[2])],[-np.sin(Pb[2]), np.cos(Pb[2])]])
        P[:2] = np.matmul(rotMatrix, P[:2])

        # Peso das espirais
        yl = -P[1] + self.r
        yr = +P[1] + self.r

        # Centros das espirais
        Pl = [P[0], P[1]-self.r]
        Pr = [P[0], P[1]+self.r]

        # Campo UVF
        if self.direction == 0:
            if np.abs(P[1]) <= self.r:
                return angl((yl*self.N_one(Pr, -1) + yr*self.N_one(Pl, +1)) / (2*self.r)) + Pb[2]
            elif P[1] < -self.r:
                return angl(self.N_one(Pr, -1)) + Pb[2]
            else:
                return angl(self.N_one(Pl, +1)) + Pb[2]
        elif self.direction == 1:
            return angl(self.M_one(Pl, +1, self.r, self.Kr_single)) + Pb[2]
        else:
            return angl(self.M_one(Pr, -1, self.r, self.Kr_single)) + Pb[2]

    def N_one(self, P, sign):
        return unit(self.alpha_one(P, sign, self.r, self.Kr))

    def M_one(self, P, sign, r, Kr):
        return unit(self.alpha_one(P, sign, r, Kr))

    def alpha_one(self, P, sign, r, Kr):
        if norml(P) >= r:
            return angl(P) + sign * np.pi/2 * (2 - (r+Kr) / (norml(P) + Kr))
        else:
            if self.spiral:
                return angl(P) + sign * np.pi/2 * np.sqrt(norml(P) / r)
            else:
                return 0