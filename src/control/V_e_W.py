from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class Teste_v_w(Control):
    """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
    def __init__(self, world):
      Control.__init__(self, world)


    def output(self, robot):
      self.v = 0
      self.old_pos = 0
      self.w = 0
      self.old_th = 0
      self.pos_obj = [0,0,0]
      self.pos_r = [0,0,0]

      if robot.field is not None:
        # self.pos_r[2] = robot.th_raw
        # self.pos_r[:2] = robot.pos
        # pos_obj[2] = robot.field.F[self.pos_r]
        # pos_obj[:2] = robot.field.Pb[:2]
        
        # Δth = pos_obj[2] - self.pos_r[2]
        # t = 1/60
        # self.w = Δth/t
        # self.v = self.w * norm(self.pos_r[:2], pos_obj[:2])
        self.pos_r[2] = 0.0
        self.pos_r[:2] = [0.0,0.0]
        self.pos_obj[2] = 0.08333333333333333333333333333333
        self.pos_obj[:2] = [0.0, 0.0]
        print(f"objective pos: {self.pos_obj}")
        print(f"robot pos: {self.pos_r}")
        
        Δth = self.pos_obj[2] - self.pos_r[2]
        ΔS = norm(self.pos_r[:2], self.pos_obj[:2])
        print()
        t = 1/60
        self.w = Δth/t
        self.v = ΔS/t

        print(f'v: {self.v} w: {self.w}')
      return (self.v, self.w)
    
    def get_error(self):

      Δth = self.pos_obj[2] - self.pos_r[2]
      t = 1/60
      self.w = Δth/t

      return self.w
    
    def get_v(self):

      self.v = self.w * norm(self.pos_r[:2], self.pos_obj[:2])

      return self.v

    def Controle():
      erro = 0
      err_sum = 0
      last_err = 0

      kp = 1
      ki = 1
      kw = 1