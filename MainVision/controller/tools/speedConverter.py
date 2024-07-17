from math import pi
from math import fabs
import numpy as np

# Constantes físicas do robô
wheel_reduction = 1
r = 0.03
L = 0.075

# Calcula maior velocidade do motor em m/s
max_tics_per_s = 70000.
encoder_resolution = 512.*19
max_motor_speed = (max_tics_per_s) / encoder_resolution * 10000

# Calcula o fator de conversão
convertion = (512*19) / 1000

def speeds2motors(v: float, w: float) -> (int, int):
  """Recebe velocidade linear e angular e retorna velocidades para as duas rodas"""

  # Computa a velocidade angular de rotação de cada roda
  vr = (v + (L/2)*w) / (2*pi*r) * wheel_reduction
  vl = (v - (L/2)*w) / (2*pi*r) * wheel_reduction
  
  #if fabs(vr) > max_motor_speed or fabs(vl) > max_motor_speed:
  #  vr = max_motor_speed * vr / max(vr, vl)
  #  vl = max_motor_speed * vl / max(vr, vl)
  
  vr *= convertion
  vl *= convertion
  
  return int(vl), int(vr)

def encodeSpeeds(v: float, w: float) -> (int, int):
  
  venc = int(v/2 * 32767)
  wenc = int(w/64 * 32767)

  return (1 if venc >= 0 else -1) * (abs(venc) % 32767), (1 if wenc >= 0 else -1) * (abs(wenc) % 32767)