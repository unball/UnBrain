import numpy as np
from tools import angl, ang, unit, norm, norml, angError, filt, sat
from . import Field


class UVF(Field):
    def __init__(self, world, Pb, robot, radius=0.1382, direction=0, spiral=True):
        super().__init__(Pb)

        self.Pb = Pb

        self.robot = robot

        self.world = world

        self.wall_x = self.world.field.marginX

        self.wall_y = self.world.field.marginY

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
        self.Kr = 0.2333

        self.Ko = 0.0003


    def F(self, P):
        return self.th(P, np.array(self.Pb))

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
        return np.exp(-(r**2/2*delta**2))
    
    def AUF(self, P, Po, Pr, Vr, Vo):

        s = self.Ko * (Vo - Vr)

        d = norm(Pr,Po)
        if d >= norml(s):
            Pvo = Po[:2] + s
        else:
            Pvo = Po[:2] + (d / norml(s)) * s
        
        return ang(Pvo, P)
    
    def th(self, P, Pb):

        R = [0,0,0,0]
        Vr = self.robot.v
        Vo = np.array([[0,0],[0,0]])
        Po = [0,0]
        v_aliado = [0,0]
        pos_aliado=[0,0]
        Pr = self.robot.pos
        Wall = [(self.wall_x, Pr[1]), (Pr[0], self.wall_y), (-self.wall_x, Pr[1]), (Pr[0], -self.wall_y)]
        
        i=0
        for robot in self.world._team:
            if robot is not None:
                if self.robot.id != robot.id:
                    v_aliado[i] = np.array(robot.v)
                    pos_aliado[i] = robot.pos
                    i+=1

        Po[0] = Wall[0]
        for pos in Wall:
            if norm(pos, P) < norm(Po[0], P):
                Po[0] = pos
        
        if pos_aliado[0] != 0 and pos_aliado[1] == 0:
            Po[1] = pos_aliado[0]
        elif pos_aliado[1] != 0 and pos_aliado[0] == 0:
            Po[1] = pos_aliado[1]
        elif pos_aliado[0] != 0 and pos_aliado[1] != 0:
            Po[1]  = pos_aliado[0] if norm(pos_aliado[0], P) < norm(pos_aliado[1], P) else pos_aliado[1]

        if abs(self.robot.pos[1]) < 0.2:
            Po[0] = Po[0] + (np.sign(Po[0][0])*0.1, 0)

        if Po[0] == Wall[0] or Po[0] == Wall[2] or (Po[0][0] - np.sign(Po[0][0])*0.1, Po[0][1]) == Wall[0] or (Po[0][0] - np.sign(Po[0][0])*0.1, Po[0][1]) == Wall[2]:
            Po[0] = [(Po[0][0]-0.02, Po[0][1]), (Po[0][0]-0.01, Po[0][1]), Po[0], (Po[0][0]+0.01, Po[0][1]), (Po[0][0]+0.02, Po[0][1])]
        else:
            Po[0] = [(Po[0][0], Po[0][1]-0.02),(Po[0][0], Po[0][1]-0.01), Po[0],(Po[0][0], Po[0][1]+0.01),(Po[0][0], Po[0][1]+0.02)]
       
        for i, pos in enumerate(Po):
            if pos != 0 and i == 1:
                R[i] = norm(self.robot.pos,pos)
            elif pos != 0:
                init = norm(Po[0][2], self.robot.pos)
                perto = Po[0][2]
                for pose in pos:
                    if norm(pose, self.robot.pos) < init:
                        init = norm(pose, self.robot.pos)
                        perto = pose
                Po[0] = perto
                R[0] = init

        Rmenor = R[0]
        ind = 0
        for i, r in enumerate(R):
            if r < Rmenor and r != 0:
                Rmenor = r
                ind = i
            
        if Rmenor > self.dmin[ind] and not Rmenor == 0:
            th = self.AUF(P, Po[ind],Pr,Vr,Vo[ind]) * self.G(Rmenor-self.dmin[ind],self.delta[ind]) + (self.TUF(P, Pb) * (1-self.G(norm(P,Pb)-self.dmin[1], self.delta_b)))
        elif not Rmenor == 0:                
            th = self.AUF(P, Po[ind],Pr,Vr,Vo[ind])
        return th