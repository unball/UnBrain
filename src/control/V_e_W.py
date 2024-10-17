from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class Teste_v_w(Control):
    """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
    def __init__(self, world, kp_w= 1, ki_w= 0, kd_w= 0):
      Control.__init__(self, world)

      self.kp_w = kp_w
      self.ki_w = ki_w
      self.kd_w = kd_w

      #twiddle const
      self.tempo = time.time()
      self.tempo_total = 0.0
      self.exec = time.time()
      self.x = 1
      self.index = 1
      self.expectate_x = 0.0
      self.expectate_y = 0.0
      self.expectate_th = 0.0

      self.v = 0
      self.old_v = 0
      self.err_v = 0
      self.old_err_v = 0
      self.sum_err_v = 0
      self.w = 0
      self.cntrl_w = 0
      self.fira_w = 0
      self.err_w = 0
      self.old_err_w = 0
      self.sum_err_w = 0
      self.pos_obj = [0,0,0]
      self.pos_r = [0,0,0]

      self.t_err = 0

    def twiddle(self, robot, kp, ki, kd, quad=False):
      # k[0] = kp
      # k[1] = ki
      # k[2] = kd
      v = 0
      w = 0
      
      self.pos_r[2] = robot.th_raw
      self.pos_r[:2] = robot.pos
      self.pos_obj = self.pos_r.copy()

      #target ultimo erro
      if self.index < 5:
        if self.x == 1 and time.time() - self.tempo < 0.7:
          self.v = 0.2
          w = 0.0

          if self.index == 1:
            self.pos_obj[0] += self.v*1/60
          elif self.index == 2:
            self.pos_obj[1] -= self.v*1/60
          elif self.index == 3:
            self.pos_obj[0] -= self.v*1/60
          elif self.index == 4:
            self.pos_obj[1] += self.v*1/60
          
        elif self.x == 1:
          self.x = 2
          self.tempo = time.time()

        elif self.x == 2 and time.time() - self.tempo < 0.314:
          self.v = 0.0
          w = 5.0

          self.pos_obj[2] -= w*1/60
          
        elif self.x == 2:
          self.x = 3
          self.tempo = time.time()

        elif self.x == 3 and time.time() - self.tempo < 0.3:
          self.v = 0.0
          w = 0.0

        elif self.x == 3:
          self.x = 1
          self.tempo = time.time()
          self.index += 1

      elif self.index < 9:
        if self.x == 1 and time.time() - self.tempo < 0.7:
          self.v = -0.2
          w = 0.0

          if self.index == 1:
            self.pos_obj[0] -= self.v*1/60
          elif self.index == 2:
            self.pos_obj[1] -= self.v*1/60
          elif self.index == 3:
            self.pos_obj[0] += self.v*1/60
          elif self.index == 4:
            self.pos_obj[1] += self.v*1/60

        elif self.x == 1:
          self.x = 2
          self.tempo = time.time()

        elif self.x == 2 and time.time() - self.tempo < 0.314:
          self.v = 0.0
          w = -5.0

          self.pos_obj[2] += w*1/60

        elif self.x == 2:
          self.x = 3
          self.tempo = time.time()

        elif self.x == 3 and time.time() - self.tempo < 0.3:
          self.v = 0.0
          w = 0.0

        elif self.x == 3:
          self.x = 1
          self.tempo = time.time()
          self.index += 1

      if self.index == 9:
        self.v = 0
        w = 0
        if quad:
          self.index = 1
          self.tempo = time.time()
          self.t_err = 0

        
      dth = self.pos_obj[2] - self.pos_r[2]
      dS = norm(self.pos_r[:2], self.pos_obj[:2])
      t = 1/60
      print(f'{self.index}\n')

      self.fira_w = robot.w
      self.old_err_w = self.err_w
      self.err_w = self.get_err(self.fira_w, w)
      self.sum_err_w += self.err_w
      if abs(self.sum_err_w) > 64.0: self.sum_err_w = 0

      if self.err_w > self.t_err:
        self.t_err = self.err_w
      
      self.cntrl_w = self.control_w(self.err_w, self.sum_err_w, self.old_err_w, kp, ki, kd)
      print(self.cntrl_w)
      print('erro: ',self.t_err, self.x)
      print(f'omega: {w}, fira w: {self.fira_w}, th: {robot.th_raw}')

      return self.v, self.cntrl_w, self.t_err

    def get_err(self, old, actual):

      err = abs(actual - old)

      return err

    def control_v(self, err, err_sum, old_err):
      kp = self.kp_w
      ki = self.ki_w
      kd = self.kd_w
    
    def control_w(self, err, err_sum, old_err, kp, ki, kd):
      

      w = kp*err + ki*err_sum + kd*(err-old_err)

      return w

    def output(self, robot):

      if robot.field is not None:
        self.pos_r[2] = robot.th_raw
        self.pos_r[:2] = robot.pos
        self.pos_obj[2] = robot.field.F(self.pos_r)
        self.pos_obj[:2] = robot.field.Pb[:2]
        
        dth = self.pos_obj[2] - self.pos_r[2]
        t = 1/60
        self.w = dth/t
        self.v = self.w * norm(self.pos_r[:2], self.pos_obj[:2])

        dth = self.pos_obj[2] - self.pos_r[2]
        dS = norm(self.pos_r[:2], self.pos_obj[:2])

        print()
        t = 1/60

        self.fira_w = self.w
        self.w = dth/t
        self.old_err_w = self.err_w
        self.err_w = self.get_err(self.fira_w, self.w)
        self.sum_err_w += self.err_w
        w = self.control_w(self.err_w, self.sum_err_w, self.old_err_w, self.kp_w, self.ki_w, self.kd_w)

        
        self.old_v = self.v
        self.v = dS/t
        self.old_err_v = self.err_v
        self.err_v = self.get_err(self.old_v,self.v)
        self.sum_err_v += self.err_v
        v = self.control_v(self.err_v, self.sum_err_v, self.old_err_v)

        print(f'v: {self.v} w1: {self.w} w2: {w}')
      return (self.v, w)