import numpy as np
from tools import angl, ang, unit, norm, norml, angError, filt, sat
from . import Field


class UVF(Field):
    def __init__(self, world, Pb, robot, radius=0.1382, direction=0, spiral=True, avoid_obstacles=True, Kr=0.2333):
        super().__init__(Pb)

        self.Pb = Pb

        self.robot = robot

        self.world = world

        self.wall_x = self.world.field.marginX # - self.world.field.xmargin

        self.wall_y = self.world.field.marginY # - self.world.field.ymargin

        self.dmin = [0.0274,0.0444,0.0444,0.0444]

        self.delta = [51,90,90,90]

        self.delta_b = 2483

        self.Pr = robot.pos

        self.Vr = np.array(robot.v)

        # Raio da espiral
        self.r = radius

        # Direção da espiral, 0 para duas espirais
        self.direction = direction

        # Habilita espiral interna, caso contrário são retas
        self.spiral = spiral

        # Constantes das espirais duplas
        self.Kr = Kr

        self.Ko = 0.0003

        self.Vo = np.zeros((5, 2))
        self.Po = np.zeros((5, 2))
        self.avoid_obstacles = avoid_obstacles

        # [HLC] Override opcional vindo da interface: sobrepõe as variáveis REAIS do UVF
        # que o usuário editou. Dict vazio/ausente = comportamento do artigo intacto.
        _ov = getattr(world, 'hlc_uvf_overrides', None)
        if _ov:
            if _ov.get('UVF_radius')     is not None: self.r = float(_ov['UVF_radius'])
            if _ov.get('UVF_Kr')         is not None: self.Kr = float(_ov['UVF_Kr'])
            if _ov.get('UVF_Ko')         is not None: self.Ko = float(_ov['UVF_Ko'])
            if _ov.get('UVF_dmin_wall')  is not None: self.dmin[0] = float(_ov['UVF_dmin_wall'])
            if _ov.get('UVF_dmin_robot') is not None: self.dmin[1:] = [float(_ov['UVF_dmin_robot'])] * 3
            if _ov.get('UVF_delta_wall') is not None: self.delta[0] = float(_ov['UVF_delta_wall'])
            if _ov.get('UVF_delta_robot')is not None: self.delta[1:] = [float(_ov['UVF_delta_robot'])] * 3
            if _ov.get('UVF_delta_b')    is not None: self.delta_b = float(_ov['UVF_delta_b'])
    def F(self, P, probe=False):
        # probe=True: avalia o campo COMO SE o robô estivesse em P (obstáculos/parede
        # relativos ao ponto amostrado). Usado só para a visualização do overlay, para
        # o desvio de parede aparecer no campo todo. No controle (P = pose do robô)
        # probe é irrelevante, então o comportamento da estratégia fica intacto.
        return self.th(P, np.array(self.Pb), probe=probe)

    def TUF(self, P, Pb):
        
        P = P.copy()

        # Ajusta o sistema de coordenadas
        cos_b = np.cos(Pb[2])
        sin_b = np.sin(Pb[2])
        dx = P[0] - Pb[0]
        dy = P[1] - Pb[1]
        
        P[0] = dx * cos_b + dy * sin_b
        P[1] = -dx * sin_b + dy * cos_b

        # Peso das espirais
        yl = -P[1] + self.r
        yr = +P[1] + self.r

        # Centros das espirais
        Pl = [P[0], P[1]-self.r]
        Pr = [P[0], P[1]+self.r]

        # Campo UVF
        if self.direction == 0:
            if P[1] < -self.r:
                return angl(self.N_one(Pr, -1)) + Pb[2]
            elif P[1] >= self.r:
                return angl(self.N_one(Pl, +1)) + Pb[2]
            else:
                return angl((yl*self.N_one(Pr, -1) + yr*self.N_one(Pl, +1)) / (2*self.r)) + Pb[2]
        elif self.direction == 1:
            return angl(self.M_one(Pl, +1, self.r, self.Kr)) + Pb[2]
        else:
            return angl(self.M_one(Pr, -1, self.r, self.Kr)) + Pb[2]

    def N_one(self, P, sign):
        return unit(self.alpha_one(P, sign, self.r, self.Kr))

    def M_one(self, P, sign, r, Kr):
        return unit(self.alpha_one(P, sign, r, Kr))

    def alpha_one(self, P, sign, r, Kr):
        if norml(P) > r:
            return angl(P) + sign * np.pi/2 * (2 - (r+Kr) / (norml(P) + Kr))
        else:
            if self.spiral:
                return angl(P) + sign * np.pi/2 * np.sqrt(norml(P) / r)
            else:
                return 0

    def G(self, r, delta):
        return np.exp(-0.5 * (r**2) * (delta**2))
    
    def AUF(self, P, Po, Pr, Vr, Vo):

        s = self.Ko * (Vo - Vr)

        d = norm(Pr,Po)
        if d >= norml(s):
            Pvo = Po[:2] + s
        else:
            Pvo = Po[:2] + (d / norml(s)) * s
        
        return ang(Pvo, P)
    
    def th(self, P, Pb, probe=False):

        if not self.avoid_obstacles:
            return self.TUF(P, Pb)

        Vr = self.robot.v
        # Na visualização (probe), ancora parede/obstáculos no ponto amostrado P, para
        # o desvio aparecer em todo o campo. No controle P == pose do robô -> idêntico.
        Pr = np.array(P[:2]) if probe else self.robot.pos

        # Candidatos de obstáculo: (pos, vel, dmin, delta). Reproduz exatamente o artigo
        # para o controle (parede índice 0 + companheiros de time índice 1); o desvio dos
        # inimigos é adicionado APENAS na visualização (probe) — o controle real não muda.
        Wall = [np.array([Pr[0], self.wall_y]), np.array([Pr[0], -self.wall_y])]
        wall_pt = Wall[0]
        for pos in Wall:
            if norm(pos, P) < norm(wall_pt, P):
                wall_pt = pos
        obstacles = [(wall_pt, np.zeros(2), self.dmin[0], self.delta[0])]

        # Companheiros de time (obstáculos reais, também no controle)
        for robot in self.world._team:
            if robot is not None and self.robot.id != robot.id:
                obstacles.append((np.array(robot.pos), np.array(robot.v), self.dmin[1], self.delta[1]))

        # Inimigos: só na visualização. Usa o mesmo dmin/delta de robô.
        if probe:
            for enemy in getattr(self.world, 'enemies', []) or []:
                if enemy is not None:
                    obstacles.append((np.array(enemy.pos), np.array(enemy.v), self.dmin[1], self.delta[1]))

        # Obstáculo mais próximo de P (empate fica com o anterior, como no artigo)
        Rmenor = float('inf')
        nearest = None
        for cand in obstacles:
            r = norm(P, cand[0])
            if r < Rmenor:
                Rmenor = r
                nearest = cand

        th = self.TUF(P, Pb)  # Default fallback
        if nearest is not None and Rmenor != 0:
            Po_n, Vo_n, dmin_n, delta_n = nearest
            if Rmenor > dmin_n:
                th = self.AUF(P, Po_n, Pr, Vr, Vo_n) * self.G(Rmenor - dmin_n, delta_n) + (self.TUF(P, Pb) * (1 - self.G(norm(P, Pb) - self.dmin[1], self.delta_b)))
            else:
                th = self.AUF(P, Po_n, Pr, Vr, Vo_n)

        return th