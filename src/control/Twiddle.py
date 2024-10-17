from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
from .V_e_W import Teste_v_w
import numpy as np
import math
import time 

class Twiddle(Control):
    """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
    def __init__(self, world):
        Control.__init__(self, world)

        #twiddle const
        self.temp = time.time()
        self.err = 0
        self.i = -1
        self.dk = [0.538265,0.049981750000000005,0.049981750000000005]
        self.target = 0
        self.twiddle = Teste_v_w(self.world).twiddle
        self.index_t = Teste_v_w(self.world).index
        self.ksi = 0.3
        self.k = [0.3767855, 0.12430794882670484, 0.03563871282511774]
        self.quad = 0
        
        # K: [0.11073450414799502, -0.025346581824602643, -0.04266883468870751]
        # dk: [0.3358946625822514, 0.530031436536443, 0.08274955973236225]
        

        self.t_err = 0

    def output(self, robot):
        if robot.field is not None:
            if time.time() - self.temp < 3 and self.i == -1:
                v = 0
                w = 0
                print(time.time() - self.temp)
                return(v,w)
            elif self.i == -1: 
                self.temp = time.time()
                self.i = 1
                return(0,0)
            
            print(f'quadrado: {self.quad}\n') 
            print(time.time() - self.temp)
            if self.quad == 0 and self.i != -1:
                v, w, err = self.teste(robot, self.quad, self.target)
                if self.i == 0:
                    self.quad += 1
                    self.i = 1
                    self.temp = time.time()
                print(f"v: {v}, w:{w}, err: {self.target}")
                return (v, w)
            elif self.quad == 1:
                v, w, err = self.teste(robot, self.quad, self.target)
                if self.i == 0:
                    self.quad += 1
                    self.i = 1
                    self.temp = time.time()
                print(f"v: {v}, w:{w}, err: {self.target}")
                return (v, w)
            elif self.quad == 2:
                v, w, err = self.teste(robot, self.quad, self.target)
                if self.i == 0:
                    self.quad = 0
                    self.i = 1
                    self.temp = time.time()
                    self.target = 0
                print(f"v: {v}, w:{w}, err: {self.target}")
                return (v, w)
        else:
            return(0,0)
    def teste(self, robot, quad, target):
  
        if time.time() - self.temp < 12.5:
            if self.i == 1:
                self.i += 1
            kp = self.k[0]
            kd = self.k[1]
            ki = self.k[2]
            print(f'K: {self.k}\n')
            print(f'dk: {self.dk}\n')
            v, w, self.err = self.twiddle(robot, kp, ki, kd)
            self.target = self.err
            return v, w, target
        elif time.time() - self.temp < 25:
            if self.i == 2:
                self.k[quad] += self.dk[quad]
                self.i += 1
                v, w, self.err = self.twiddle(robot, self.k[0], self.k[1], self.k[2], True)
            kp = self.k[0]
            kd = self.k[1]
            ki = self.k[2]
            print(f'K: {self.k}\n')
            print(f'dk: {self.dk}\n')
            v, w, self.err = self.twiddle(robot, kp, ki, kd)
            return v, w, target
        elif self.err < target and self.i == 3:
            self.target = self.err
            self.dk[quad] *= 1 + self.ksi
            self.i = 0
            v, w, self.err = self.twiddle(robot, self.k[0], self.k[1], self.k[2], True)
            return v, w, target
        elif self.i == 3 or self.i == 4:
            if time.time() - self.temp < 37.5:
                if self.i == 3:
                    self.k[quad] -= 2*self.dk[quad]
                    self.i += 1
                    v, w, self.err = self.twiddle(robot, self.k[0], self.k[1], self.k[2], True)
                kp = self.k[0]
                kd = self.k[1]
                ki = self.k[2]
                print(f'K: {self.k}\n')
                print(f'dk: {self.dk}\n')
                v, w, self.err = self.twiddle(robot, kp, ki, kd)
                return v, w, target
            elif self.err < target:
                self.target = self.err
                self.dk[quad] *= 1 + self.ksi
                self.i = 0
                v, w, self.err = self.twiddle(robot, self.k[0], self.k[1], self.k[2], True)
                return v, w, target
            else:
                self.k[quad] = self.dk[quad]
                self.dk[quad] *= 1 - self.ksi
                self.i = 0
                v, w, self.err = self.twiddle(robot, self.k[0], self.k[1], self.k[2], True)
                return v, w, target
        return 0, 0, target
