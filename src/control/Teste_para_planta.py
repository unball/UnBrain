from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class Teste(Control):
    """Controle unificado para o Univector Field, utiliza o ângulo definido pelo campo como referência \\(\\theta_d\\)."""
    def __init__(self, world):
      Control.__init__(self, world)
      self.tempo = time.time()
      self.tempo_total = 0.0
      self.exec = time.time()
      self.expectate_x = 0.0
      self.expectate_y = 0.0
      self.expectate_th = 0.0
      self.x = 1
      self.index = 1
      self.arquivo_teste = open('/home/maranhas/UnBall/UnBrain/teste.txt', 'a')

    def output(self, robot):
      # print(time.time() - self.tempo )
      # print(robot.th_raw)
      v = 0.0
      w = 0.0

      if self.index < 5:
        if self.x == 1 and time.time() - self.tempo < 0.7:
          v = 0.2
          w = 0.0
          if self.index == 1:
            self.expectate_x += v*1/60
          elif self.index == 2:
            self.expectate_y += v*1/60
          elif self.index == 3:
            self.expectate_x -= v*1/60
          elif self.index == 4:
            self.expectate_y -= v*1/60
        elif self.x == 1 and not time.time() - self.tempo < 0.7:
          self.x = 2
          self.tempo = time.time()
        elif self.x == 2 and time.time() - self.tempo < 0.314:
          v = 0.0
          w = 5.0
          self.expectate_th += w*1/60
        elif self.x == 2 and not time.time() - self.tempo < 0.314:
          self.x = 3
          self.tempo = time.time()
        elif self.x == 3 and time.time() - self.tempo < 0.5:
          v = 0.0
          w = 0.0
        elif self.x == 3 and not time.time() - self.tempo < 0.5:
          self.x = 1
          self.tempo = time.time()
          self.index += 1

      if 4 < self.index < 9:
        if self.x == 1 and time.time() - self.tempo < 0.7:
          v = -0.2
          w = 0.0
          if self.index == 1:
            self.expectate_x -= v*1/60
          elif self.index == 2:
            self.expectate_y -= v*1/60
          elif self.index == 3:
            self.expectate_x += v*1/60
          elif self.index == 4:
            self.expectate_y += v*1/60
        elif self.x == 1 and not time.time() - self.tempo < 0.7:
          self.x = 2
          self.tempo = time.time()
        elif self.x == 2 and time.time() - self.tempo < 0.314:
          v = 0.0
          w = -5.0
          self.expectate_th -= w*1/60
        elif self.x == 2 and not time.time() - self.tempo < 0.314:
          self.x = 3
          self.tempo = time.time()
        elif self.x == 3 and time.time() - self.tempo < 0.5:
          v = 0.0
          w = 0.0
        elif self.x == 3 and not time.time() - self.tempo < 0.5:
          self.x = 1
          self.tempo = time.time()
          self.index += 1
      if time.time() - self.exec > 1/60:
        self.tempo_total += time.time() - self.exec
        self.arquivo_teste.write(f'{robot.x} {robot.y} {robot.th_raw} {v} {w} {self.expectate_x} {self.expectate_y} {self.expectate_th} {self.tempo_total}\n')
        self.exec = time.time()
      if robot.spin == 0: return (v, w)
      else: return (0, 60 * robot.spin)