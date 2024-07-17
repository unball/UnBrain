import numpy as np

def norm(p0: tuple, p1: tuple):
  """Calcula a distância entre as tuplas `p0` e `p1` no plano"""
  return np.sqrt((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)

def norml(p0: tuple):
  """Calcula a norma de `p0"""
  return np.sqrt((p0[0])**2+(p0[1])**2)

def ang(p0: tuple, p1: tuple):
  """Calcula o ângulo entre as tuplas `p0` e `p1` no plano, este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p1[1]-p0[1], p1[0]-p0[0])

def angl(p0: tuple):
  """Calcula o ângulo da tupla `p0` no plano este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p0[1], p0[0])

def sat(x: float, amp: float):
  """Satura um número real `x` entre `amp` e `-amp`"""
  return max(min(x, amp), -amp)

def filt(x: float, amp: float):
  if np.abs(x) > np.abs(amp): return 0
  else: return x

def fixAngle(angle: float):
  if abs(angle) > np.pi/2:
    return (angle + np.pi/2) % (np.pi) - np.pi/2
  else:
    return angle

def angError(reference: float, current: float) -> float:
  """Calcula o erro angular entre `reference` e `current` de modo que este erro esteja no intervalo de \\((-\\pi,\\pi]\\) e o sinal do erro indique qual deve ser a orientação para seguir a referência, de modo que positivo é anti-horário e negativo é horário"""
  diff = np.arccos(np.cos(reference-current))
  sign = (np.sin(reference-current) >= 0)*2-1
  return sign * diff
    
def adjustAngle(angle: float) -> float:
  """Pega um ângulo em \\(\\mathbb{R}\\) e leva para o correspondente em \\((-\\pi,\\pi]\\)"""
  return angError(angle, 0)

def unit(angle):
  """Retorna um vetor unitário de ângulo `angle` no formato de numpy array"""
  return np.array([np.cos(angle), np.sin(angle)])
  
def bestAngError(reference: float, current: float, robot) -> float:
  err1 = angError(reference, current)
  err2 = angError(reference, current+np.pi)
  
  if robot.velmod < 0.05:
    if abs(err1) <= abs(err2): return err1, 1
    else: return err2, -1
  else:
    if robot.dir == 1: return err1, 1
    else: return err2, -1
  
def shift(data, array):
    return [data] + array[:-1]

def derivative(F, x, d=0.00001, *args):
  return (F(x+d, *args) - F(x, *args)) / d

def insideEllipse(r, a, b, rm):
  """ Retorna se a posição r está dentro da elipse de parâmetros a, b e centro rm"""
  return ((r[0]-rm[0])/a)**2+((r[1]-rm[1])/b)**2 < 1

def insideRect(r, rm, s):
  return np.all(r-rm < s)

def projectLine(r, v, xline):
  return ((xline-r[0])/v[0])*v[1] + r[1]