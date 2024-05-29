
import numpy as np
from tools import angl, unit, norml, angError, filt, sat
from . import Field

class UVF(Field):
    def __init__(self, Pb, radius=0.13, direction=0, spiral=True, Kr=0.03, Kr_single=0.03, nullgamma=False, singleObstacle=False):
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

        self.singleObstacle = singleObstacle

    def th_one(self, P, Pb):
        tuf = self.TUF_one(P, Pb=Pb)

        # # Cria obstáculo pontual
        if self.singleObstacle:
            auf, R = self.AUF(P, self.Pr, self.Vr, self.Po, self.Vo)

            if R <= self.dmin:
                uvf = auf
            else:
                uvf = auf * self.G(R-self.dmin, self.delta) + tuf * (1-self.G(R-self.dmin, self.delta))    
        else:
            uvf = tuf

        return uvf

    def TUF(self, P, Pb=None):
        P = P.copy()

        # Permite uso de Pb alternativo
        if Pb is None: Pb = self.Pb

        # Ajusta o sistema de coordenadas
        Pb = np.array([Pb])
        P[:2] = P[:2]-Pb.T[:2]
        rotMatrix = np.array([[np.cos(Pb[0][2]), np.sin(Pb[0][2])],[-np.sin(Pb[0][2]), np.cos(Pb[0][2])]])
        P[:2] = np.matmul(rotMatrix, P[:2])

        # Campo UVF
        uvf = np.zeros_like(P[0])

        # Regiões do campo
        c1 = np.abs(P[1]) <= self.r
        c2 = P[1] < -self.r
        c3 = P[1] > self.r


        # Peso das espirais
        yl = -P[1][c1] + self.r
        yr = +P[1][c1] + self.r

        # Centros das espirais
        Pl = np.array([P[0], P[1]-self.r])
        Pr = np.array([P[0], P[1]+self.r])

        # Gera cada região
        if self.direction == 0:
            uvf[c1] = angl((yl*self.N(Pr.T[c1].T, -1) + yr*self.N(Pl.T[c1].T, +1)) / (2*self.r))
            uvf[c2] = angl(self.N(Pr.T[c2].T, -1))
            uvf[c3] = angl(self.N(Pl.T[c3].T, +1))
        elif self.direction == 1:
            uvf = angl(self.M(Pl, +1, self.r, self.Kr_single))
        elif self.direction == -1:
            uvf = angl(self.M(Pr, -1, self.r, self.Kr_single))

        # Ajusta o sistema de coordenadas
        return uvf + Pb[0][2]

    def TUF_one(self, P, Pb=None):
        P = P.copy()

        # Permite uso de Pb alternativo
        if Pb is None: Pb = self.Pb

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
    def F(self, P, Pb=None, retnparray=False):
        P = np.array(P)
        if len(P.shape) == 1: return self.th_one(P, Pb)

        uvf = self.th(P, Pb)

        if uvf.size == 1 and not(retnparray): return uvf[0]
        return uvf


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